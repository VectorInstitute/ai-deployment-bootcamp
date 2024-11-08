resource "aws_sagemaker_feature_group" "example" {
  feature_group_name             = "${var.feature_group_name}"
  record_identifier_feature_name = "id"
  event_time_feature_name        = "id" # You can add a timestamp to your feautre or use their identifier
  role_arn                       = aws_iam_role.sagemaker_execution_role.arn

  feature_definition {
    feature_name = "id"
    feature_type = "Fractional"
  }
  feature_definition {
    feature_name = "seq_0"
    feature_type = "String"
  }
  feature_definition {
    feature_name = "seq_1"
    feature_type = "String"
  }
  online_store_config {
    enable_online_store = true
  }
  
}