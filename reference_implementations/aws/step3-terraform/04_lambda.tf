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

resource "aws_iam_role_policy" "lambda_logs_policy" {
  name = "BertParaphraseModelLambdaRoleTFLogsPolicy"
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
  name = "BertParaphraseModelLambdaRoleTFSageMakerPolicy"
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

resource "aws_lambda_function" "my_lambda_function" {
  filename         = "./lambda.zip"
  function_name    = "bert-paraphrase-tf"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  source_code_hash = filebase64sha256("lambda.zip")
#   timeout          = 300

  layers = [
    "arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:38"
  ]
  timeout = 900
  environment {
    variables = {
      ENDPOINT_NAME = "${var.sagemaker_endpoint_name}"
    }
  }
}