resource "aws_iam_role" "lambda_role" {
  name = "BertParaphraseModelLambdaRoleTF"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# aws_iam_role_policy: For creating inline, role-specific policies.
resource "aws_iam_role_policy" "lambda_logs_policy" {
  name = "lambda_role_logs_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams",
            "logs:PutLogEvents",
            "logs:GetLogEvents",
            "logs:FilterLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_sagemaker_policy" {
  name = "lambda_role_sagemaker_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sagemaker:InvokeEndpoint"
        Resource = "arn:aws:sagemaker:${var.region}:${local.aws_account_id}:endpoint/*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_sagemaker_featurestore_policy" {
  name = "lambda_role_sagemaker_featurestore_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "sagemaker:GetRecord",
          "sagemaker:PutRecord",
          "sagemaker:ListFeatureGroups",
          "sagemaker:BatchGetRecord"
        ]
        Resource = "arn:aws:sagemaker:${var.region}:${local.aws_account_id}:feature-group/*"
      }
    ]
  })
}

# Attach AmazonRedshiftDataFullAccess policy to the role
# aws_iam_policy_attachment: For attaching existing managed policies 
# (either AWS-managed or your own custom policies) to roles, users, or groups.
resource "aws_iam_policy_attachment" "redshift_data_access" {
  name       = "lambda_role_redshift_data_access_attachment"
  roles      = [aws_iam_role.lambda_role.id]
  policy_arn = "arn:aws:iam::aws:policy/AmazonRedshiftFullAccess"
}

# resource "aws_iam_policy_attachment" "sqs_access" {
#   name       = "lambda_role_redshift_data_access_attachment"
#   roles      = [aws_iam_role.lambda_role.id]
#   policy_arn = "arn:aws:iam::aws:policy/AWSLambdaSQSQueueExecutionRole"
# }

resource "aws_iam_role_policy" "lambda_sqs_policy" {
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"  # Add this line
        ]
        Resource = aws_sqs_queue.my_queue.arn
      }
    ]
  })
}


resource "aws_lambda_function" "my_lambda_function" {
  filename         = "./lambda.zip"
  function_name    = "bert-paraphrase-tf"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  source_code_hash = filebase64sha256("lambda.zip")
  timeout          = 300

  layers = [
    "arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:38"
  ]
  environment {
    variables = {
      ENDPOINT_NAME = "${var.sagemaker_endpoint_name}"
      FEATURE_GROUP_NAME = "${var.feature_group_name}"
      REDSHIFT_URL = "${aws_redshift_cluster.my_redshift_cluster.endpoint}:${aws_redshift_cluster.my_redshift_cluster.port}"
      REDSHIFT_USER = "${aws_redshift_cluster.my_redshift_cluster.master_username}"
      CLUSTER_ID = "${aws_redshift_cluster.my_redshift_cluster.id}"
      DB_NAME = "${var.db_name}"
    }
  }
}
