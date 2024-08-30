resource "aws_sagemaker_model" "model" {
  name = var.sagemaker_model_name
  execution_role_arn = aws_iam_role.sagemaker_execution_role.arn
  container {
    image          = var.sagemaker_container_repo_url
    model_data_url = var.sagemaker_model_data_s3_url
    mode           = var.sagemaker_model_mode
    environment = {
      "SAGEMAKER_CONTAINER_LOG_LEVEL" = "20"
      "SAGEMAKER_PROGRAM"             = "inference.py"
      "SAGEMAKER_REGION"              = "${var.region}"
      "SAGEMAKER_SUBMIT_DIRECTORY"    = "/opt/ml/model/code"
    }

    
  }
}

resource "aws_sagemaker_endpoint_configuration" "ec" {
  name = var.sagemaker_endpoint_conf_name

  production_variants {
    variant_name           = var.sagemaker_endpoint_conf_variant_name
    model_name             = aws_sagemaker_model.model.name
    initial_instance_count = var.sagemaker_model_instance_count
    instance_type          = var.sagemaker_model_instance_type
  }

  tags = merge(
    local.common_tags,
    { "Name" = "${local.prefix}-${var.sagemaker_endpoint_conf_name}" }
  )
}

resource "aws_sagemaker_endpoint" "e" {
  name                 = var.sagemaker_endpoint_name
  endpoint_config_name = aws_sagemaker_endpoint_configuration.ec.name

  tags = merge(
    local.common_tags,
    { "Name" = "${local.prefix}-${var.sagemaker_endpoint_name}" }
  )
}