resource "aws_api_gateway_rest_api" "rest_api" {
  name        = var.rest_api_name
  description = var.rest_api_description

  tags = merge(
    local.common_tags,
    { "Name" = "${local.prefix}-${var.rest_api_name}" }
  )
}

resource "aws_iam_role" "api_gateway_role" {
  name = "api_gateway_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_resource" "predict_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "predict"
}

resource "aws_api_gateway_resource" "predict_id_resource" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  parent_id   = aws_api_gateway_resource.predict_resource.id
  path_part   = "{id}"
}


resource "aws_api_gateway_method" "api_method" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "ANY"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_api_gateway_method" "predict_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  resource_id   = aws_api_gateway_resource.predict_id_resource.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.id" = true
  }
}



resource "aws_api_gateway_integration" "api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.api_resource.id
  http_method             = aws_api_gateway_method.api_method.http_method
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.my_lambda_function.invoke_arn
  integration_http_method = "ANY"
  credentials             = aws_iam_role.api_gateway_role.arn

  cache_key_parameters = ["method.request.path.proxy"]

  timeout_milliseconds = 29000
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

resource "aws_api_gateway_integration" "predict_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.predict_id_resource.id
  http_method             = aws_api_gateway_method.predict_id_get.http_method
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.my_lambda_function.invoke_arn
  integration_http_method = "POST"
  credentials             = aws_iam_role.api_gateway_role.arn

  request_parameters = {
    "integration.request.path.id" = "method.request.path.id"
  }
}


# lambda execution permission for api gateway
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.my_lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  # source_arn    = "arn:aws:execute-api:${var.region}:${local.aws_account_id}:${aws_api_gateway_rest_api.rest_api.id}/*/${aws_api_gateway_method.api_method.http_method}${aws_api_gateway_resource.api_resource.path}"
}

resource "aws_iam_role_policy" "api_gateway_invoke_lambda" {
  role = aws_iam_role.api_gateway_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = aws_lambda_function.my_lambda_function.arn
      }
    ]
  })
}

resource "aws_api_gateway_deployment" "stage" {
  depends_on = [
    aws_api_gateway_integration.api_integration,
    aws_api_gateway_integration.predict_id_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = "dev"
}