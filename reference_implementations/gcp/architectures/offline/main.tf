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

resource "google_project_service" "run" {
  project = var.project
  service = "run.googleapis.com"
}

resource "google_project_service" "cloudbuild" {
  project = var.project
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "cloudresourcemanager" {
  project = var.project
  service = "cloudresourcemanager.googleapis.com"
}

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

resource "google_project_iam_member" "storage_bucket_reader" {
  project = var.project
  role    = "roles/storage.insightsCollectorService"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "ai_platform_user" {
  project = var.project
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "big_query_user" {
  project = var.project
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "big_query_data_editor" {
  project = var.project
  role    = "roles/bigquery.dataEditor"
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

resource "google_pubsub_topic" "input_queue" {
  name                       = "${var.project}-${var.env}-input-queue"
  message_retention_duration = "86600s"
}

resource "google_storage_bucket" "gcf_source" {
  name                        = "${var.project}-${var.env}-gcf-source"
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
  name        = "${var.project}-${var.env}-ml-api"
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
      MODEL          = var.model
      ENV            = var.env
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.input_queue.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_project_service.run,
    google_project_service.cloudbuild,
    google_project_service.cloudfunctions,
    google_project_service.eventarc,
    google_storage_bucket_object.ml_api,
  ]
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
