variable "project" { }
variable "zone" { }

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
    zone    = var.zone
}

resource "google_compute_network" "vpc_network" {
    name = "${var.project}-network"
}

resource "google_compute_instance" "vm_instance" {
    name         = "${var.project}-ml-api"
    machine_type = "f1-micro"
    boot_disk {
        initialize_params {
            image = "debian-cloud/debian-11"
        }
    }
    network_interface {
        network = google_compute_network.vpc_network.name
        access_config {
        }
    }
}
