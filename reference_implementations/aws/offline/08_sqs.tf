# Create an SQS Queue
resource "aws_sqs_queue" "inference_queue" {
  name                       = "inference_queue"
  visibility_timeout_seconds  = 300
  message_retention_seconds   = 86400
}

# Allow the SQS queue to trigger the Lambda function
resource "aws_lambda_event_source_mapping" "sqs_lambda_trigger" {
  event_source_arn  = aws_sqs_queue.inference_queue.arn
  function_name     = aws_lambda_function.inference_lambda_function.arn  # Lambda function you want to trigger
  batch_size        = 10   # Number of records to send to the Lambda function at once
  enabled           = true
}

