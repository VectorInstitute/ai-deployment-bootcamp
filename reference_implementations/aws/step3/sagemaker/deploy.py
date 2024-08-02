import boto3
from sagemaker import Session

def deploy_model(
        image_uri: str, 
        role_arn: str, 
        endpoint_name: str, 
        instance_type: str, 
        accelerator_type: str):
    """
    Deploys a model to a SageMaker real-time endpoint with GPU support.

    Args:
        image_uri (str): URI of the Docker image in ECR.
        role_arn (str): IAM role ARN for the model execution.
        endpoint_name (str): Desired name for the SageMaker endpoint.
        instance_type (str): AWS instance type for the endpoint (e.g., ml.g4dn.xlarge).
        accelerator_type (str): Type of accelerator (e.g., ml.g4dn.xlarge).
    """

    session = Session()

    # Create a SageMaker model
    primary_container = {
        'Image': image_uri,
        'ModelDataUrl': 's3://sagemaker-us-east-1-artifacts/huggingface/transformers/facebook/bart-large-mnli'
    }  # Adjust region if needed

    create_model_response = session.create_model(
        ModelName=endpoint_name,
        ExecutionRoleArn=role_arn,
        PrimaryContainer=primary_container
    )

    # Create an endpoint configuration
    create_endpoint_config_response = session.create_endpoint_config(
        name=endpoint_name + '-config',
        production_variants=[
            {
                'VariantName': 'AllTraffic',    
                'ModelName': create_model_response['ModelArn'],
                'InitialInstanceCount': 1,
                'InstanceType': instance_type,
                'AcceleratorType': accelerator_type,
                'AcceleratorCount': 1,  # Adjust if needed
                'MinInstanceCount': 0,  # Minimum of 0 instances (autoscaling down)
                'MaxInstanceCount': 10,  # Maximum of 10 instances (autoscaling up)
            }
        ]
    )

    # Create a SageMaker endpoint
    create_endpoint_response = session.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=create_endpoint_config_response['EndpointConfigArn']
    )

    print(create_endpoint_response)

# # Example usage
# image_uri = 'your-ecr-uri:latest'  # Replace with your ECR image URI
# role_arn = 'arn:aws:iam::your-account-id:role/your-role'
# endpoint_name = 'my-bart-endpoint'
# instance_type = 'ml.g4dn.xlarge'
# accelerator_type = 'ml.g4dn.xlarge'

# deploy_model(image_uri, role_arn, endpoint_name, instance_type, accelerator_type)






# SageMaker Endpoint Scaling Behavior with InitialInstanceCount=1 and MinInstanceCount=0

# Yes, if you set InitialInstanceCount to 1 and MinInstanceCount to 0, your SageMaker endpoint will eventually scale down to 0 instances if there are no requests for a sustained period.
# Factors Affecting Scale-Down Time:

# The exact time it takes for the endpoint to scale down to 0 instances depends on several factors:

#     SageMaker's Auto-Scaling Policy: This determines how aggressively SageMaker scales down instances in response to decreased traffic.
#     Instance Type: The type of instance you're using can influence the scale-down time.
#     Region-Specific Configuration: SageMaker's behavior might vary slightly across different AWS regions.

# Typically, it takes several minutes of inactivity before SageMaker starts the process of scaling down an instance. However, the exact time frame can be longer, especially for larger instance types or in regions with high utilization.
# Additional Considerations:

#     Warm-Up Time: When the endpoint scales back up after a period of inactivity, there might be a warm-up period before it can start serving requests efficiently.
#     Cost Optimization: While scaling down to 0 instances can save costs, it's essential to balance cost savings with potential performance impacts during traffic spikes.
#     Monitoring: Closely monitor your endpoint's performance and resource utilization to fine-tune scaling parameters.

# To optimize your endpoint's behavior, you might consider:

#     Customizing Auto-Scaling Policies: Explore using custom auto-scaling policies to fine-tune the scaling behavior based on your specific workload.
#     Instance Warm-Up: Implement strategies to pre-warm instances to reduce initial latency when scaling up.
#     Cost-Benefit Analysis: Evaluate the trade-offs between cost savings and potential performance impacts.

# By carefully considering these factors, you can effectively manage the scaling behavior of your SageMaker endpoint to meet your application's requirements.
