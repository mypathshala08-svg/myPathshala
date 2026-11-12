variable "project" { type = string }
provider "google" {
  project = var.project
  region  = "asia-south1"
}
resource "google_cloud_run_v2_service" "canteen" {
  name                = "canteen"
  location            = "asia-south1"
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels              = { project = "canteen" }
  template {
    containers { image = "us-docker.pkg.dev/cloudrun/container/hello" }
    scaling { max_instance_count = 3 }
  }
}
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.canteen.name
  location = google_cloud_run_v2_service.canteen.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
resource "google_storage_bucket" "receipts" {
  name                        = "canteen-receipts-${var.project}"
  location                    = "asia-south1"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = true
  lifecycle_rule {
    condition { age = 30 }
    action { type = "Delete" }
  }
}
output "url" { value = google_cloud_run_v2_service.canteen.uri }
