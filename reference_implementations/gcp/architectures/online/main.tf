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
  account_id = "${var.short_project_prefix}-sa"
  display_name = "${var.project} Service Account"
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

# Service accounts for team members
resource "google_service_account" "aj_sa" {
  account_id   = "${var.short_project_prefix}-aj-sa"
  display_name = "AJ Service Account"
  project      = var.project
}

resource "google_service_account" "my_sa" {
  account_id   = "${var.short_project_prefix}-my-sa"
  display_name = "MY Service Account"
  project      = var.project
}

resource "google_service_account" "db_sa" {
  account_id   = "${var.short_project_prefix}-db-sa"
  display_name = "DB Service Account"
  project      = var.project
}

resource "google_service_account" "co_sa" {
  account_id   = "${var.short_project_prefix}-co-sa"
  display_name = "CO Service Account"
  project      = var.project
}

resource "google_service_account" "lb_sa" {
  account_id   = "${var.short_project_prefix}-lb-sa"
  display_name = "LB Service Account"
  project      = var.project
}

resource "google_service_account" "ha_sa" {
  account_id   = "${var.short_project_prefix}-ha-sa"
  display_name = "HA Service Account"
  project      = var.project
}

# Assigning permissions to service accounts for aj
resource "google_project_iam_member" "storage_object_viewer_aj" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.aj_sa.email}"
}

resource "google_project_iam_member" "ai_platform_user_aj" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.aj_sa.email}"
}

resource "google_project_iam_member" "compute_instances_get_aj" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.aj_sa.email}"
}

# Assigning permissions to service accounts for my
resource "google_project_iam_member" "storage_object_viewer_my" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.my_sa.email}"
}

resource "google_project_iam_member" "ai_platform_user_my" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.my_sa.email}"
}

resource "google_project_iam_member" "compute_instances_get_my" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.my_sa.email}"
}

# Assigning permissions to service accounts for db
resource "google_project_iam_member" "storage_object_viewer_db" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.db_sa.email}"
}

resource "google_project_iam_member" "ai_platform_user_db" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.db_sa.email}"
}

resource "google_project_iam_member" "compute_instances_get_db" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.db_sa.email}"
}

# Assigning permissions to service accounts for co
resource "google_project_iam_member" "storage_object_viewer_co" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.co_sa.email}"
}

resource "google_project_iam_member" "ai_platform_user_co" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.co_sa.email}"
}

resource "google_project_iam_member" "compute_instances_get_co" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.co_sa.email}"
}

# Assigning permissions to service accounts for lb
resource "google_project_iam_member" "storage_object_viewer_lb" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.lb_sa.email}"
}

resource "google_project_iam_member" "ai_platform_user_lb" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.lb_sa.email}"
}

resource "google_project_iam_member" "compute_instances_get_lb" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.lb_sa.email}"
}

# Assigning permissions to service accounts for ha
resource "google_project_iam_member" "storage_object_viewer_ha" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.ha_sa.email}"
}

resource "google_project_iam_member" "ai_platform_user_ha" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.ha_sa.email}"
}

resource "google_project_iam_member" "compute_instances_get_ha" {
  project = var.project
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.ha_sa.email}"
}


### END SERVICE ACCOUNT PERMISSIONS

resource "google_bigquery_dataset" "database" {
  dataset_id    = "${local.project_prefix}_database"
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
  name    = "allow-ssh"
  network = google_compute_network.my_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  target_tags = [
    "sshfw",
    "${var.short_project_prefix}-arooj",
    "${var.short_project_prefix}-mingchen",
    "${var.short_project_prefix}-daniel",
    "${var.short_project_prefix}-chike",
    "${var.short_project_prefix}-louisphilippe",
    "${var.short_project_prefix}-hadi"
  ]

  source_ranges = ["0.0.0.0/0"] # Be cautious with this; it allows access from any IP. Adjust as necessary.
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
  name                        = "${var.project}-api-source"
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
  name                      = "${var.project}-ml-api"
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
  name   = "${local.project_prefix}_featurestore"
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

resource "google_compute_firewall" "allow_jupyter" {
  name    = "allow-jupyter"
  network = google_compute_network.my_network.name

  allow {
    protocol = "tcp"
    ports    = ["8080", "8888"]  // Add any other ports you use for JupyterLab
  }

  // Adjust the source_ranges as needed for security. 
  // This example allows access from any IP, which might not be suitable for all use cases.
  source_ranges = ["0.0.0.0/0"]
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
  service_account_id = "projects/${var.project}/serviceAccounts/${google_service_account.sa.email}"
  role               = "roles/iam.serviceAccountUser"
  members            = [for member in var.team_members : "user:${member}"]
}

locals {
  team_info = { for email in var.team_members : email => {
    email = email,
    username = lower(replace(replace(split("@", email)[0], ".", "-"), "_", "-")),
    shortened = "${var.short_project_prefix}-${substr(replace(split("@", email)[0], ".", "-"), 0, 1)}${
      length(split("-", replace(split("@", email)[0], ".", "-"))) > 1 ? 
      substr(split("-", replace(split("@", email)[0], ".", "-"))[1], 0, 1) : 
      ""}"
  }}
}

resource "google_service_account_iam_binding" "aj_sa_binding" {
  service_account_id = google_service_account.aj_sa.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "user:arooj_ahmed.qureshi@bell.ca",
    "user:louisphilippe.bosse@bell.ca"
  ]
}

resource "google_service_account_iam_binding" "my_sa_binding" {
  service_account_id = google_service_account.my_sa.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "user:mingchen.yang@bell.ca",
    "user:louisphilippe.bosse@bell.ca"
  ]
}

resource "google_service_account_iam_binding" "db_sa_binding" {
  service_account_id = google_service_account.db_sa.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "user:daniel.bucci@bell.ca",
    "user:louisphilippe.bosse@bell.ca"
  ]
}

resource "google_service_account_iam_binding" "co_sa_binding" {
  service_account_id = google_service_account.co_sa.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "user:chike.odenigbo@bell.ca",
    "user:louisphilippe.bosse@bell.ca"
  ]
}

resource "google_service_account_iam_binding" "lb_sa_binding" {
  service_account_id = google_service_account.lb_sa.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "user:louisphilippe.bosse@bell.ca"
  ]
}

resource "google_service_account_iam_binding" "ha_sa_binding" {
  service_account_id = google_service_account.ha_sa.name
  role               = "roles/iam.serviceAccountUser"
  members            = [
    "user:hadi.abdi_ghavidel@bell.ca",
    "user:louisphilippe.bosse@bell.ca"
  ]
}

# Assigns the roles/compute.osLoginExternalUser role to the user arooj_ahmed.qureshi@bell.ca
# This role allows the specified user to use OS Login to authenticate to instances
# where OS Login is enabled.
#resource "google_project_iam_member" "user_os_login_arooj" {
#  project = var.project
#  role    = "roles/compute.osLoginExternalUser"
#  member  = "user:arooj_ahmed.qureshi@bell.ca"
#}

# Assigns the roles/compute.osLoginExternalUser role to the user mingchen.yang@bell.ca
#resource "google_project_iam_member" "user_os_login_mingchen" {
#  project = var.project
#  role    = "roles/compute.osLoginExternalUser"
#  member  = "user:mingchen.yang@bell.ca"
#}

# Assigns the roles/compute.osLoginExternalUser role to the user daniel.bucci@bell.ca
#resource "google_project_iam_member" "user_os_login_daniel" {
#  project = var.project
#  role    = "roles/compute.osLoginExternalUser"
#  member  = "user:daniel.bucci@bell.ca"
#}

# Assigns the roles/compute.osLoginExternalUser role to the user chike.odenigbo@bell.ca
#resource "google_project_iam_member" "user_os_login_chike" {
#  project = var.project
#  role    = "roles/compute.osLoginExternalUser"
#  member  = "user:chike.odenigbo@bell.ca"
#}

# Assigns the roles/compute.osLoginExternalUser role to the user louisphilippe.bosse@bell.ca
#resource "google_project_iam_member" "user_os_login_louisphilippe" {
#  project = var.project
#  role    = "roles/compute.osLoginExternalUser"
#  member  = "user:louisphilippe.bosse@bell.ca"
#}

# Assigns the roles/compute.osLoginExternalUser role to the user hadi.abdi_ghavidel@bell.ca
#resource "google_project_iam_member" "user_os_login_hadi" {
#  project = var.project
#  role    = "roles/compute.osLoginExternalUser"
#  member  = "user:hadi.abdi_ghavidel@bell.ca"
#}

resource "google_notebooks_instance" "instance_arooj" {
  name          = "${var.short_project_prefix}-workbench-arooj"
  location      = "${var.region}-a"
  machine_type  = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = [
    "arooj_ahmed.qureshi@bell.ca"
  ]
  service_account = "${google_service_account.aj_sa.email}"

  install_gpu_driver = true
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip     = false
  no_proxy_access  = false

  network = google_compute_network.my_network.id
  subnet  = google_compute_subnetwork.my_subnetwork.id

  labels = {
    project = var.project
  }

  metadata = {
    terraform = "true"
  }
  service_account_scopes = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]

  tags = ["${var.short_project_prefix}-arooj"]

  disk_encryption = "GMEK"
  
  desired_state   = "INACTIVE"
}


resource "google_notebooks_instance" "instance_mingchen" {
  name          = "${var.short_project_prefix}-workbench-mingchen"
  location      = "${var.region}-a"
  machine_type  = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = [
    "mingchen.yang@bell.ca"
  ]
  service_account = "${google_service_account.my_sa.email}"

  install_gpu_driver = true
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip     = false
  no_proxy_access  = false

  network = google_compute_network.my_network.id
  subnet  = google_compute_subnetwork.my_subnetwork.id

  labels = {
    project = var.project
  }

  metadata = {
    terraform = "true"
  }
  service_account_scopes = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]

  tags = ["${var.short_project_prefix}-mingchen"]

  disk_encryption = "GMEK"
  
  desired_state   = "INACTIVE"
}

resource "google_notebooks_instance" "instance_daniel" {
  name          = "${var.short_project_prefix}-workbench-daniel"
  location      = "${var.region}-a"
  machine_type  = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = [
    "daniel.bucci@bell.ca"
  ]
  service_account = "${google_service_account.db_sa.email}"

  install_gpu_driver = true
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip     = false
  no_proxy_access  = false

  network = google_compute_network.my_network.id
  subnet  = google_compute_subnetwork.my_subnetwork.id

  labels = {
    project = var.project
  }

  metadata = {
    terraform = "true"
  }
  service_account_scopes = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]

  tags = ["${var.short_project_prefix}-daniel"]

  disk_encryption = "GMEK"
  
  desired_state   = "INACTIVE"
}

resource "google_notebooks_instance" "instance_chike" {
  name          = "${var.short_project_prefix}-workbench-chike"
  location      = "${var.region}-a"
  machine_type  = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = [
    "chike.odenigbo@bell.ca"
  ]
  service_account = "${google_service_account.co_sa.email}"

  install_gpu_driver = true
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip     = false
  no_proxy_access  = false

  network = google_compute_network.my_network.id
  subnet  = google_compute_subnetwork.my_subnetwork.id

  labels = {
    project = var.project
  }

  metadata = {
    terraform = "true"
  }
  service_account_scopes = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]

  tags = ["${var.short_project_prefix}-chike"]

  disk_encryption = "GMEK"
  
  desired_state   = "INACTIVE"
}
#louisphilippe_bosse@cloudshell:~$ gcloud projects add-iam-policy-binding bell-canada-inc --member='user:louisphilippe.bosse@bell.ca' --role='roles/compute.osLoginExternalUser'
#ERROR: (gcloud.projects.add-iam-policy-binding) INVALID_ARGUMENT: Request contains an invalid argument.
resource "google_notebooks_instance" "instance_louisphilippe" {
  name          = "${var.short_project_prefix}-workbench-louisphilippe"
  location      = "${var.region}-a"
  machine_type  = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = ["louisphilippe.bosse@bell.ca"]
  service_account = "${google_service_account.lb_sa.email}"

  install_gpu_driver = true
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip     = false
  no_proxy_access  = false

  network = google_compute_network.my_network.id
  subnet  = google_compute_subnetwork.my_subnetwork.id

  labels = {
    project = var.project
  }

  metadata = {
    terraform = "true"
  }

  service_account_scopes = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]

  tags = ["${var.short_project_prefix}-louisphilippe"]

  disk_encryption = "GMEK"
  
  desired_state   = "INACTIVE"
}

resource "google_notebooks_instance" "instance_hadi" {
  name          = "${var.short_project_prefix}-notebooks-hadi"
  location      = "${var.region}-a"
  machine_type  = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  instance_owners = [
    "hadi.abdi_ghavidel@bell.ca"
  ]
  service_account = "${google_service_account.ha_sa.email}"

  install_gpu_driver = true
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb = 110

  no_public_ip     = false
  no_proxy_access  = false

  network = google_compute_network.my_network.id
  subnet  = google_compute_subnetwork.my_subnetwork.id

  labels = {
    project = var.project
  }

  metadata = {
    terraform = "true"
  }

  service_account_scopes = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email"
  ]

  tags = ["${var.short_project_prefix}-hadi"]

  disk_encryption = "GMEK"
  
  desired_state   = "INACTIVE"
}