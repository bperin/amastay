import boto3
from datetime import datetime


def list_endpoints(status_filter=None):
    """
    List all SageMaker endpoints with their details
    Args:
        status_filter (str, optional): Filter endpoints by status ('InService', 'Creating', etc.)
    """
    sagemaker_client = boto3.client("sagemaker")

    # Get all endpoints
    endpoints = sagemaker_client.list_endpoints()["Endpoints"]

    # Print header
    print("\n{:<40} {:<15} {:<20} {:<25}".format("Endpoint Name", "Status", "Instance Type", "Creation Time"))
    print("-" * 100)

    # Get detailed information for each endpoint
    endpoint_details = []
    for endpoint in endpoints:
        desc = sagemaker_client.describe_endpoint(EndpointName=endpoint["EndpointName"])

        # Skip if status filter is set and doesn't match
        if status_filter and desc["EndpointStatus"] != status_filter:
            continue

        # Get instance type from endpoint config
        config = sagemaker_client.describe_endpoint_config(EndpointConfigName=desc["EndpointConfigName"])
        instance_type = config["ProductionVariants"][0]["InstanceType"]

        # Format creation time
        creation_time = desc["CreationTime"].strftime("%Y-%m-%d %H:%M:%S")

        # Print endpoint details
        print("{:<40} {:<15} {:<20} {:<25}".format(desc["EndpointName"], desc["EndpointStatus"], instance_type, creation_time))

        endpoint_details.append([desc["EndpointName"], desc["EndpointStatus"], instance_type, creation_time])

    return endpoint_details


if __name__ == "__main__":
    # List all endpoints
    print("\nAll Endpoints:")
    list_endpoints()

    # List only active endpoints
    print("\nActive Endpoints:")
    list_endpoints(status_filter="InService")
