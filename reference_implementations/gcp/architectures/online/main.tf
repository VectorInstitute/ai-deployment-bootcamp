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

variable "team_members" {
  description = "List of team member identifiers"
  type        = list(string)
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

resource "google_compute_firewall" "ssh" {
  name    = "ssh-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["sshfw"]
}

resource "google_compute_firewall" "webserver" {
  name    = "http-https-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["webserverfw"]
}

resource "google_compute_address" "static_ip" {
  name = "website-address"
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

resource "google_vertex_ai_featurestore" "default" {
  name   = "${local.project_prefix}_${var.env}_featurestore"
  region = var.region

  online_serving_config {
    fixed_node_count = 1
  }

  force_destroy = true
}

resource "google_vertex_ai_featurestore_entitytype" "data_entity" {
  name         = "data_entity"
  featurestore = google_vertex_ai_featurestore.default.id

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }

  depends_on = [google_vertex_ai_featurestore.default]
}

resource "google_vertex_ai_featurestore_entitytype_feature" "data_feature" {
  name       = "data_feature"
  entitytype = google_vertex_ai_featurestore_entitytype.data_entity.id
  value_type = "STRING"
}

resource "google_compute_network" "my_network" {
  name                    = "${var.short_project_prefix}-network"
  auto_create_subnetworks = false
  project                 = var.project
}

resource "google_compute_subnetwork" "my_subnetwork" {
  name          = "${var.short_project_prefix}-subnetwork"
  network       = google_compute_network.my_network.id
  region        = var.region
  ip_cidr_range = "10.0.1.0/24"
  project       = var.project
}

resource "google_compute_address" "static" {
  name    = "${var.short_project_prefix}-static-ip"
  region  = var.region
  project = var.project
}

resource "google_service_account_iam_binding" "act_as_permission" {
  service_account_id = "projects/${var.project}/serviceAccounts/${var.user}"
  role               = "roles/iam.serviceAccountUser"
  members            = [for member in var.team_members : "user:${member}"]
}

resource "google_workbench_instance" "instance" {
  for_each = toset(var.team_members)

  name     = "${var.short_project_prefix}-workbench-${each.key}"
  location = "${var.region}-a"
  project  = var.project

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type       = "NVIDIA_TESLA_T4"
      core_count = 1
    }

    shielded_instance_config {
      enable_secure_boot         = true
      enable_vtpm                = true
      enable_integrity_monitoring = true
    }

    disable_public_ip = false

    service_accounts {
      email = "${each.value}@service-account.com" # Example of dynamic email construction
    }

    boot_disk {
      disk_size_gb    = 310
      disk_type       = "PD_SSD"
      disk_encryption = "CMEK"
      kms_key         = "my-crypto-key"
    }

    data_disks {
      disk_size_gb    = 330
      disk_type       = "PD_SSD"
      disk_encryption = "CMEK"
      kms_key         = "my-crypto-key"
    }

    network_interfaces {
      network      = google_compute_network.my_network.id
      subnet       = google_compute_subnetwork.my_subnetwork.id
      nic_type     = "GVNIC"
      access_configs {
        external_ip = google_compute_address.static.address
      }
    }

    metadata = {
      terraform = "true"
    }

    enable_ip_forwarding = true

    tags = ["${var.short_project_prefix}-${each.key}"]
  }

  disable_proxy_access = true

  instance_owners = [each.value]

  labels = {
    project = var.project
    env     = var.env
  }

  desired_state = "ACTIVE"
}