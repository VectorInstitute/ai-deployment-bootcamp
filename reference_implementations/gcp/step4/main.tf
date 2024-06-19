variable "region" {
    type = string
}
variable "project" {
    type = string
}

variable "user" {
    type = string
}

variable "scriptpath" {
    type = string
}

variable "publickeypath" {
    type = string
    default = "~/.ssh/id_rsa.pub"
}

provider "google" {
  project = var.project
  region  = var.region
}

resource "google_service_account" "sa" {
  account_id = "${var.project}-sa"
  display_name = "${var.project} Service Account"
}

resource "google_project_iam_member" "cloud_sql_client" {
  project = var.project
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.sa.email}"
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

resource "google_sql_database_instance" "master" {
  name                = "${var.project}-db-instance"
  database_version    = "POSTGRES_14"
  region              = var.region
  root_password       = "t9CHsm3a"
  deletion_protection = false
  settings {
    tier = "db-custom-2-7680"
  }
}

resource "google_sql_database" "database" {
  name      = "${var.project}-database"
  instance  = google_sql_database_instance.master.name
}

resource "google_sql_user" "users" {
  name     = "root"
  instance = google_sql_database_instance.master.name
  password = "t9CHsm3a"
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

resource "google_compute_instance" "ml-api-server" {
  name         = "ml-api-vm"
  machine_type = "e2-micro" 
  zone         = "${var.region}-a" 
  tags         = ["sshfw","webserverfw"]
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
  }

  metadata_startup_script = file(var.scriptpath)
  service_account {
    email = google_service_account.sa.email
    scopes = ["sql-admin", "cloud-platform"]
  }

  depends_on = [ google_compute_firewall.ssh, google_compute_firewall.webserver ]
  
}

output "public_ip_address" {
  value = google_compute_address.static_ip.address
}

output "ssh_access_via_ip" {
  value = "ssh ${var.user}@${google_compute_address.static_ip.address}"
}

resource "google_vertex_ai_featurestore" "default" {
  name   = "featurestore"
  region = var.region

  online_serving_config {
    fixed_node_count = 1
  }

  force_destroy = true
}

resource "google_vertex_ai_featurestore_entitytype" "data_entity" {
  name = "data_entity"
  featurestore = google_vertex_ai_featurestore.default.id

  monitoring_config {
    snapshot_analysis {
      disabled = false
    }
  }

  depends_on = [google_vertex_ai_featurestore.default]
}

resource "google_vertex_ai_featurestore_entitytype_feature" "data_feature" {
  name     = "data_feature"
  entitytype = google_vertex_ai_featurestore_entitytype.data_entity.id
  value_type = "STRING"
}
