resource "aws_ecr_repository" "banking_api" {
  name                 = "${var.project_name}-api"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
}
