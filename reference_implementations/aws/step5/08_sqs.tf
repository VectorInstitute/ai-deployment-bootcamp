# Create an SQS Queue
resource "aws_sqs_queue" "my_queue" {
  name                       = "my_queue"
  visibility_timeout_seconds  = 300
  message_retention_seconds   = 86400
}

# Allow the SQS queue to trigger the Lambda function
resource "aws_lambda_event_source_mapping" "sqs_lambda_trigger" {
  event_source_arn  = aws_sqs_queue.my_queue.arn
  function_name     = aws_lambda_function.my_lambda_function.arn  # Lambda function you want to trigger
  batch_size        = 10   # Number of records to send to the Lambda function at once
  enabled           = true
}

# # IAM policy to allow SQS to invoke Lambda
# resource "aws_iam_role_policy" "lambda_sqs_policy" {
#   role = aws_iam_role.lambda_role.id

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = "sqs:SendMessage"
#         Resource = aws_sqs_queue.my_queue.arn
#       }
#     ]
#   })
# }
