variable "region" {
    type = string
}
variable "project" {
    type = string
}

variable "user" {
    type = string
}

variable "endpoint" {
    type = string
}

### BEGIN ENABLING APIS

resource "google_project_service" "cloudfunctions" {
  project = var.project
  service = "cloudfunctions.googleapis.com"
}

resource "google_project_service" "eventarc" {
  project = var.project
  service = "eventarc.googleapis.com"
}

### END ENABLING APIS

provider "google" {
  project = var.project
  region  = var.region
}

data "google_project" "project" {
  project_id = var.project
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

resource "google_sql_user" "db_user" {
  name     = "root"
  instance = google_sql_database_instance.master.name
  password = "t9CHsm3a"
}

resource "google_sql_database" "database" {
  name       = "${var.project}-database"
  instance   = google_sql_database_instance.master.name
  depends_on = [ google_sql_user.db_user ]
}

resource "google_pubsub_topic" "input_queue" {
  name                       = "${var.project}-input-queue"
  message_retention_duration = "86600s"
}

resource "google_storage_bucket" "gcf_source" {
  name                        = "${var.project}-gcf-source"
  location                    = "US"
  uniform_bucket_level_access = true
}

data "archive_file" "ml_api" {
  type        = "zip"
  output_path = "${path.module}/ml-api.zip"
  source_dir  = "ml-api/"
}

resource "google_storage_bucket_object" "ml_api" {
  name   = "ml-api-${data.archive_file.ml_api.output_md5}.zip"  # the md5 will force a redeploy whenever the code changes
  bucket = google_storage_bucket.gcf_source.name
  source = data.archive_file.ml_api.output_path
  depends_on = [ google_storage_bucket.gcf_source, data.archive_file.ml_api ]
}

resource "google_cloudfunctions2_function" "default" {
  name        = "${var.project}-ml-api"
  location    = var.region
  description = "ML API to process input messages"

  build_config {
    runtime               = "python39"
    entry_point           = "process"
    source {
      storage_source {
        bucket = google_storage_bucket.gcf_source.name
        object = google_storage_bucket_object.ml_api.name
      }
    }
  }

  service_config {
    max_instance_count             = 3
    min_instance_count             = 1
    available_memory               = "512M"
    timeout_seconds                = 60
    ingress_settings               = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    service_account_email          = google_service_account.sa.email
    environment_variables = {
      ENDPOINT_ID    = var.endpoint
      PROJECT_ID     = var.project
      PROJECT_NUMBER = data.google_project.project.number
      REGION         = var.region
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.input_queue.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_project_service.cloudfunctions,
    google_project_service.eventarc,
    google_storage_bucket_object.ml_api,
  ]
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
