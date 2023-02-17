# ECR
resource "aws_ecr_repository" "license_returner" {
  name = "${var.prefix}-license_returner"
  image_scanning_configuration {
    scan_on_push = true
  }
  image_tag_mutability = "MUTABLE"
  encryption_configuration {
    encryption_type = "AES256"
  }
}

# CloudWatch Logs
resource "aws_cloudwatch_log_group" "generate_cw_log_group_license_returner" {
  name              = "/aws/batch/job/${var.prefix}-license-returner/"
  retention_in_days = 120
}

# Job Definition
resource "aws_batch_job_definition" "generate_batch_jd_uploader" {
  name                  = "${var.prefix}-license-returner"
  type                  = "container"
  container_properties  = <<CONTAINER_PROPERTIES
  {
    "image": "${aws_ecr_repository.license_returner.repository_url}:latest",
    "logConfiguration": {
        "logDriver" : "awslogs",
        "options": {
            "awslogs-group" : "${aws_cloudwatch_log_group.generate_cw_log_group_license_returner.name}"
        }
    },
    "resourceRequirements" : [
        { "type": "MEMORY", "value": "256"},
        { "type": "VCPU", "value": "1" }
    ],
    "jobRoleArn": "${aws_iam_role.aws_batch_service_role_license_returner.arn}"
  }
  CONTAINER_PROPERTIES
  platform_capabilities = ["EC2"]
  propagate_tags        = true
  retry_strategy {
    attempts = 3
  }
}

# Job role
resource "aws_iam_role" "aws_batch_service_role_license_returner" {
  name = "${var.prefix}-batch-service-role-license-returner"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  permissions_boundary = "arn:aws:iam::${local.account_id}:policy/NGAPShRoleBoundary"
}

resource "aws_iam_role_policy_attachment" "aws_batch_service_role_policy_attach" {
  role       = aws_iam_role.aws_batch_service_role_license_returner.name
  policy_arn = aws_iam_policy.batch_service_role_policy_license_returner.arn
}

resource "aws_iam_policy" "batch_service_role_policy_license_returner" {
  name        = "${var.prefix}-batch-service-role-policy-license-returner"
  description = "Provides access to: SSM for license returner containers."
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AllowSSMGetPut",
        "Effect" : "Allow",
        "Action" : [
          "ssm:GetParameter",
          "ssm:PutParameter",
          "ssm:DeleteParameters"
        ],
        "Resource" : "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/${var.prefix}*"
      }
    ]
  })
}