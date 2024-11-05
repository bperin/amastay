import boto3
import time


def deploy_endpoint(model_name, instance_type="ml.g5.2xlarge", instance_count=1):
    sagemaker_client = boto3.client("sagemaker")

    # Configuration names will match the model name
    endpoint_config_name = model_name
    endpoint_name = model_name

    try:
        # Delete existing endpoint config if it exists
        try:
            sagemaker_client.delete_endpoint_config(EndpointConfigName=endpoint_config_name)
            print(f"Deleted existing endpoint config: {endpoint_config_name}")
        except sagemaker_client.exceptions.ClientError:
            pass

        # Delete existing endpoint if it exists
        try:
            sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            print(f"Deleted existing endpoint: {endpoint_name}")
            waiter = sagemaker_client.get_waiter("endpoint_deleted")
            waiter.wait(EndpointName=endpoint_name)
        except sagemaker_client.exceptions.ClientError:
            pass

        # Create endpoint configuration
        print(f"Creating endpoint configuration: {endpoint_config_name}")
        sagemaker_client.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[
                {
                    "VariantName": "AllTraffic",
                    "ModelName": model_name,
                    "InstanceType": instance_type,
                    "InitialInstanceCount": instance_count,
                }
            ],
        )

        # Create endpoint
        print(f"Creating endpoint: {endpoint_name}")
        sagemaker_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name,
        )

        # Wait for endpoint to be in service
        print("Waiting for endpoint to be ready...")
        waiter = sagemaker_client.get_waiter("endpoint_in_service")
        waiter.wait(EndpointName=endpoint_name)

        print(f"Endpoint {endpoint_name} successfully deployed!")
        return endpoint_name

    except Exception as e:
        print(f"Error deploying endpoint: {str(e)}")
        raise


if __name__ == "__main__":
    MODEL_NAME = "meta-llama-llama-3-2-11b-vision-instruct"
    INSTANCE_TYPE = "ml.g5.2xlarge"
    INSTANCE_COUNT = 1

    deploy_endpoint(model_name=MODEL_NAME, instance_type=INSTANCE_TYPE, instance_count=INSTANCE_COUNT)
