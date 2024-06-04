variable "project" { }
variable "zone" { }
variable "step" { }

terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "4.51.0"
        }
    }
}

provider "google" {
    project = var.project
    zone    = "${var.zone}-a"
}

resource "google_compute_network" "default" {
    name                    = "${var.project}-${var.step}-network"
    auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "default" {
    name          = "${var.project}-${var.step}-vpc-subnet"
    ip_cidr_range = "10.124.0.0/28"
    region        = var.zone
    network       = google_compute_network.default.id
}

resource "google_project_service" "vpc" {
    service            = "vpcaccess.googleapis.com"
    disable_on_destroy = false
}


resource "google_vpc_access_connector" "default" {
    name          = "${var.step}-vpc-connector"
    region        = var.zone
    subnet {
        name = google_compute_subnetwork.default.name
    }
    depends_on = [
        google_project_service.vpc
    ]

}

resource "google_compute_router" "default" {
    name     = "${var.project}-${var.step}-ip-router"
    network  = google_compute_network.default.name
    region   = google_compute_subnetwork.default.region
}

resource "google_compute_address" "default" {
    name     = "${var.project}-${var.step}-ip-addr"
    region   = google_compute_subnetwork.default.region
}

resource "google_compute_router_nat" "default" {
    name     = "${var.project}-${var.step}-nat"
    router   = google_compute_router.default.name
    region   = google_compute_subnetwork.default.region

    nat_ip_allocate_option = "MANUAL_ONLY"
    nat_ips                = [google_compute_address.default.self_link]

    source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
    subnetwork {
        name                    = google_compute_subnetwork.default.id
        source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
    }
}

resource "google_cloud_run_v2_service" "ml_api" {
    name     = "${var.project}-${var.step}-ml-api"
    location = google_compute_subnetwork.default.region

    template {
        containers {
            image = "${var.zone}-docker.pkg.dev/${var.project}/${var.project}-docker-repo/${var.project}-${var.step}:latest"
        }
        scaling {
            max_instance_count = 1
        }
        vpc_access {
            connector = google_vpc_access_connector.default.id
            egress    = "ALL_TRAFFIC"
        }
    }
    ingress = "INGRESS_TRAFFIC_ALL"
}
