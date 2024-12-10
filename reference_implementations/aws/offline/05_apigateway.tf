resource "aws_api_gateway_rest_api" "rest_api" {
  name        = "${local.prefix}-${var.rest_api_name}"
  description = var.rest_api_description

  tags = merge(
    local.common_tags,
    { "Name" = "${local.prefix}-${var.rest_api_name}" }
  )
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
  uri                     = aws_lambda_function.inference_lambda_function.invoke_arn
  integration_http_method = "ANY"

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
  uri                     = aws_lambda_function.inference_lambda_function.invoke_arn
  integration_http_method = "POST"

  request_parameters = {
    "integration.request.path.id" = "method.request.path.id"
  }
}


# lambda execution permission for api gateway
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inference_lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:${local.aws_account_id}:${aws_api_gateway_rest_api.rest_api.id}/*/${aws_api_gateway_method.api_method.http_method}${aws_api_gateway_resource.api_resource.path}"
}

resource "aws_lambda_permission" "apigw_lambda_predict_id" {
  statement_id  = "AllowExecutionFromAPIGatewayPredictID"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inference_lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${local.aws_account_id}:${aws_api_gateway_rest_api.rest_api.id}/dev/GET/predict/*"
}


resource "aws_api_gateway_deployment" "stage" {
  depends_on = [
    aws_api_gateway_integration.api_integration,
    aws_api_gateway_integration.predict_id_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  stage_name  = "dev"
}