resource "aws_iam_role" "sagemaker_execution_role" {
  name = "${local.prefix}-SagemakerModelExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "sagemaker_execution_role_policy" {
  name        = "${local.prefix}-sagemaker-execution-role-policy"
  description = "Policy for SageMaker model"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { # models and endpoint access
        Action = [
          "sagemaker:CreateModel",
          "sagemaker:CreateEndpointConfig",
          "sagemaker:CreateEndpoint",
          "sagemaker:DeleteEndpoint",
          "sagemaker:InvokeEndpoint",
          "sagemaker:UpdateEndpoint",
          "sagemaker:StopEndpoint",
          "sagemaker:DeleteEndpointConfig",
          "sagemaker:DeleteModel",
          "sagemaker:DescribeEndpoint",
          "sagemaker:DescribeEndpointConfig",
          "sagemaker:DescribeModel",
          "sagemaker:AddTags"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:sagemaker:${var.region}:${local.aws_account_id}:endpoint-config/*",
          "arn:aws:sagemaker:${var.region}:${local.aws_account_id}:model/*",
          "arn:aws:sagemaker:${var.region}:${local.aws_account_id}:endpoint/*",
          "arn:aws:sagemaker:${var.region}:${local.aws_account_id}:app/*"
        ]
      },
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Effect = "Allow"
        # TODO: give permission to access S3 buckets - replace with your bucket names
        Resource = [
          "arn:aws:s3:::sagemaker-endpoint-deploy-tf-state-vector",
          "arn:aws:s3:::sagemaker-endpoint-deploy-tf-state-vector/*",
          "arn:aws:s3:::sagemaker-us-east-1-025066243062",
          "arn:aws:s3:::sagemaker-us-east-1-025066243062/*"
        ]
      },
      { # reading/writing logs
        Action = [
          "logs:CreateLogDelivery",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DeleteLogDelivery",
          "logs:Describe*",
          "logs:GetLogDelivery",
          "logs:GetLogEvents",
          "logs:ListLogDeliveries",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
          "logs:PutResourcePolicy",
          "logs:UpdateLogDelivery",
          "logs:FilterLogEvents"
        ]
        Effect = "Allow"
        Resource = "*"
      },
      { # cloud watch
        Action = [
          "cloudwatch:DeleteAlarms",
          "cloudwatch:DescribeAlarms",
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:PutMetricData"
        ]
        Effect = "Allow"
        Resource = "*"
      },
      {
        "Effect" : "Allow",
        "Action" : "ecr:GetAuthorizationToken",
        "Resource" : "*"
      },
      {
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchGetImage",
          "ecr:GetLifecyclePolicy",
          "ecr:GetLifecyclePolicyPreview",
          "ecr:ListTagsForResource",
          "ecr:DescribeImageScanFindings"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:ecr:${var.region}:763104351884:repository/*",
        ]
      },
      { # feature store
        Action = [
            "glue:GetTable",
            "glue:UpdateTable"
        ],
        Effect = "Allow",
        Resource = [
            "arn:aws:glue:*:*:catalog",
            "arn:aws:glue:*:*:database/sagemaker_featurestore",
            "arn:aws:glue:*:*:table/sagemaker_featurestore/*"
        ]
        }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_execution_role_policy_attachment" {
  policy_arn = aws_iam_policy.sagemaker_execution_role_policy.arn
  role       = aws_iam_role.sagemaker_execution_role.name
}