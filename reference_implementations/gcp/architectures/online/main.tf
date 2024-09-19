variable "region" {
  type = string
}

variable "project" {
  type = string
}

variable "short_project_prefix" {
  type = string
}

variable "env" {
  type = string
}

variable "user" {
  type = string
}

variable "scriptpath" {
  type    = string
  default = "./ml-api/startup.sh"
}

variable "publickeypath" {
  type = string
}

variable "endpoint" {
  type = string
}

variable "model" {
  type = string
}

variable "schemas_folder" {
  type = string
}

locals {
  # cleaning up project name to make it friendly to some IDs
  project_prefix = replace(var.project, "-", "_")
}

### BEGIN ENABLING APIS

resource "google_project_service" "cloudresourcemanager" {
  project = var.project
  service = "cloudresourcemanager.googleapis.com"
}

### END ENABLING APIS

provider "google" {
  project = var.project
  region  = var.region
}

data "google_project" "project" {
  project_id = var.project
}

### BEGIN SERVICE ACCOUNT PERMISSIONS

resource "google_service_account" "sa" {
  account_id = "${var.short_project_prefix}-${var.env}-sa"
  display_name = "${var.project}-${var.env} Service Account"
}

resource "google_project_iam_member" "storage_object_viewer" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "ai_platform_user" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "compute_instances_get" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

### END SERVICE ACCOUNT PERMISSIONS

resource "google_bigquery_dataset" "database" {
  dataset_id    = "${local.project_prefix}_${var.env}_database"
  location      = "US"
}

resource "google_bigquery_table" "data_table" {
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.database.dataset_id
  table_id            = "data_table"
  schema              = file("${var.schemas_folder}/data.json")
}

resource "google_bigquery_table" "predictions_table" {
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.database.dataset_id
  table_id            = "predictions_table"
  schema              = file("${var.schemas_folder}/predictions.json")
}

resource "google_bigquery_table" "ground_truth_table" {
  deletion_protection = false
  dataset_id          = google_bigquery_dataset.database.dataset_id
  table_id            = "ground_truth_table"
  schema              = file("${var.schemas_folder}/groundtruth.json")
}

resource "google_compute_firewall" "ssh" {
  name    = "${var.project}-${var.env}-ssh-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["sshfw"]
}

resource "google_compute_firewall" "webserver" {
  name    = "${var.project}-${var.env}-http-https-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["webserverfw"]
}

resource "google_compute_address" "static_ip" {
  name = "${var.project}-${var.env}-website-address"
}

resource "google_storage_bucket" "api_source" {
  name                        = "${var.project}-${var.env}-api-source"
  location                    = "US"
  uniform_bucket_level_access = true
}

data "archive_file" "ml_api" {
  type        = "zip"
  output_path = "${path.module}/ml-api.zip"
  source_dir  = "ml-api/"
}

resource "google_storage_bucket_object" "ml_api" {
  name   = "ml-api.zip"
  bucket = google_storage_bucket.api_source.name
  source = data.archive_file.ml_api.output_path
  depends_on = [ google_storage_bucket.api_source, data.archive_file.ml_api ]
}

resource "google_compute_instance" "ml-api-server" {
  name                      = "${var.project}-${var.env}-ml-api"
  machine_type              = "e2-micro"
  zone                      = "${var.region}-a"
  tags                      = ["sshfw", "webserverfw", "http-server"]
  allow_stopping_for_update = true

   
  boot_disk { 
    initialize_params {
      image = "ubuntu-2004-lts"
    }
  }

  network_interface {
    network = "default"
    
    access_config {
      nat_ip = google_compute_address.static_ip.address
    }
  }

  metadata = {
    ssh-keys = "${var.user}:${file(var.publickeypath)}"
    endpoint = var.endpoint
    model    = var.model
    env      = var.env
  }

  metadata_startup_script = file(var.scriptpath)

  service_account {
    email  = google_service_account.sa.email
    scopes = ["sql-admin", "cloud-platform"]
  }

  depends_on = [ google_compute_firewall.ssh, google_compute_firewall.webserver, data.archive_file.ml_api ]
  
}

output "public_ip_address" {
  value = google_compute_address.static_ip.address
}

output "ssh_access_via_ip" {
  value = "ssh ${var.user}@${google_compute_address.static_ip.address}"
}

resource "google_bigquery_dataset" "featurestore_dataset" {
  dataset_id    = "${local.project_prefix}_${var.env}_featurestore_dataset"
  location      = "US"
}

resource "google_bigquery_table" "featurestore_table" {
  deletion_protection = false
  dataset_id = google_bigquery_dataset.featurestore_dataset.dataset_id
  table_id   = "featurestore_table"
  schema     = file("${var.schemas_folder}/featurestore.json")
}

resource "google_vertex_ai_feature_online_store" "featurestore" {
  name   = "${local.project_prefix}_${var.env}_featurestore"
  region = var.region
  optimized {}
  force_destroy = true
}

resource "google_vertex_ai_feature_online_store_featureview" "featureview" {
  name                 = "featureview"
  region               = var.region
  feature_online_store = google_vertex_ai_feature_online_store.featurestore.name
  sync_config {
    cron = "* * * * *" // sync every minute
  }
  big_query_source {
    uri               = "bq://${google_bigquery_table.featurestore_table.project}.${google_bigquery_table.featurestore_table.dataset_id}.${google_bigquery_table.featurestore_table.table_id}"
    entity_id_columns = ["entity_id"]
  }
}
