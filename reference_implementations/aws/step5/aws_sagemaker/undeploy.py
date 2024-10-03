import boto3

def undeploy_all_models(endpoint_name):
    client = boto3.client('sagemaker')

    # Get endpoint configuration
    response = client.describe_endpoint(EndpointName=endpoint_name)
    production_variants = response['ProductionVariants']

    # Undeploy each model
    for variant in production_variants:
        model_name = variant['ModelName']
        client.update_endpoint(
            EndpointName=endpoint_name,
            ProductionVariants=[
                {
                    'VariantName': variant['VariantName'],
                    'InitialInstanceCount': 0,
                    'InstanceType': variant['InstanceType']
                }
            ]
        )
    # Delete entire endpoint
    client.delete_endpoint(EndpointName=endpoint_name)