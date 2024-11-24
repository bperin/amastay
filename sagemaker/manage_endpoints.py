import boto3
import argparse
from datetime import datetime


def list_endpoints(status_filter=None):
    """
    List all SageMaker endpoints with their details
    Args:
        status_filter (str, optional): Filter endpoints by status ('InService', 'Creating', etc.)
    Returns:
        list: List of endpoint details
    """
    sagemaker_client = boto3.client("sagemaker")
    endpoints = []
    paginator = sagemaker_client.get_paginator("list_endpoints")

    for page in paginator.paginate():
        for endpoint in page["Endpoints"]:
            try:
                endpoint_name = endpoint["EndpointName"]
                status = endpoint["EndpointStatus"]

                if status_filter and status.lower() != status_filter.lower():
                    continue

                # Get endpoint details first
                endpoint_desc = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
                config_name = endpoint_desc.get("EndpointConfigName")

                if not config_name:
                    instance_type = "Unknown"
                else:
                    # Get endpoint config
                    try:
                        config_response = sagemaker_client.describe_endpoint_config(EndpointConfigName=config_name)
                        variant = config_response["ProductionVariants"][0]
                        instance_type = variant.get("InstanceType", "Serverless") if "ServerlessConfig" in variant else variant.get("InstanceType", "Unknown")
                    except Exception as e:
                        print(f"Warning: Could not get config for {endpoint_name}: {str(e)}")
                        instance_type = "Unknown"

                creation_time = endpoint["CreationTime"]
                endpoints.append({"name": endpoint_name, "status": status, "instance_type": instance_type, "creation_time": creation_time})
            except Exception as e:
                print(f"Warning: Error processing endpoint {endpoint.get('EndpointName', 'unknown')}: {str(e)}")
                continue

    return endpoints


def list_endpoint_configs():
    """List all SageMaker endpoint configurations"""
    sagemaker_client = boto3.client("sagemaker")
    configs = sagemaker_client.list_endpoint_configs()["EndpointConfigs"]

    print("\n{:<40} {:<25}".format("Config Name", "Creation Time"))
    print("-" * 65)

    config_details = []
    for config in configs:
        desc = sagemaker_client.describe_endpoint_config(EndpointConfigName=config["EndpointConfigName"])
        creation_time = desc["CreationTime"].strftime("%Y-%m-%d %H:%M:%S")
        print("{:<40} {:<25}".format(desc["EndpointConfigName"], creation_time))
        config_details.append({"name": desc["EndpointConfigName"], "creation_time": creation_time})

    return config_details


def delete_endpoint_config(config_name):
    """Delete a specific endpoint configuration"""
    sagemaker_client = boto3.client("sagemaker")
    try:
        print(f"Deleting endpoint configuration: {config_name}")
        sagemaker_client.delete_endpoint_config(EndpointConfigName=config_name)
        return True
    except Exception as e:
        print(f"Error deleting endpoint configuration {config_name}: {str(e)}")
        return False


def delete_endpoint(endpoint_name):
    """Delete a specific endpoint"""
    sagemaker_client = boto3.client("sagemaker")
    try:
        print(f"Deleting endpoint: {endpoint_name}")
        sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        return True
    except Exception as e:
        print(f"Error deleting endpoint {endpoint_name}: {str(e)}")
        return False


def cleanup_endpoint_resources(endpoint_name, delete_config=True):
    """Clean up both endpoint and optionally its configuration"""
    sagemaker_client = boto3.client("sagemaker")

    try:
        # First get the endpoint config name
        endpoint_desc = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        config_name = endpoint_desc["EndpointConfigName"]

        # Delete endpoint first
        if delete_endpoint(endpoint_name) and delete_config:
            # Then delete config if requested
            delete_endpoint_config(config_name)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Manage SageMaker endpoints and configurations")
    parser.add_argument("--list", action="store_true", help="List all endpoints")
    parser.add_argument("--list-configs", action="store_true", help="List all endpoint configurations")
    parser.add_argument("--status", choices=["InService", "Creating", "Failed"], help="Filter endpoints by status")
    parser.add_argument("--delete", action="store_true", help="Delete endpoints (will prompt for confirmation)")
    parser.add_argument("--delete-configs", action="store_true", help="Delete endpoint configurations")
    parser.add_argument("--endpoint", help="Specific endpoint name to delete")
    parser.add_argument("--config", help="Specific endpoint configuration to delete")
    parser.add_argument("--keep-configs", action="store_true", help="When deleting endpoints, keep their configurations")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    # List endpoints
    if args.list:
        endpoints = list_endpoints(status_filter=args.status)

    # List configurations
    if args.list_configs:
        configs = list_endpoint_configs()

    # Handle endpoint deletion
    if args.delete:
        if args.endpoint:
            # Delete specific endpoint
            if input(f"\nConfirm deletion of endpoint '{args.endpoint}'? (y/N): ").lower() == "y":
                cleanup_endpoint_resources(args.endpoint, not args.keep_configs)
        else:
            # Show endpoints and ask which to delete
            endpoints = list_endpoints(status_filter=args.status)
            print("\nAvailable endpoints for deletion:")
            for i, endpoint in enumerate(endpoints, 1):
                print(f"{i}. {endpoint['name']} ({endpoint['status']})")

            try:
                choice = input("\nEnter number(s) to delete (comma-separated) or 'all', or press Enter to cancel: ")
                if choice.lower() == "all":
                    if input("Are you sure you want to delete ALL endpoints? (y/N): ").lower() == "y":
                        for endpoint in endpoints:
                            cleanup_endpoint_resources(endpoint["name"], not args.keep_configs)
                elif choice.strip():
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    for idx in indices:
                        if 0 <= idx < len(endpoints):
                            cleanup_endpoint_resources(endpoints[idx]["name"], not args.keep_configs)
                        else:
                            print(f"Invalid index: {idx + 1}")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")

    # Handle configuration deletion
    if args.delete_configs:
        if args.config:
            # Delete specific config
            if input(f"\nConfirm deletion of configuration '{args.config}'? (y/N): ").lower() == "y":
                delete_endpoint_config(args.config)
        else:
            # Show configs and ask which to delete
            configs = list_endpoint_configs()
            print("\nAvailable configurations for deletion:")
            for i, config in enumerate(configs, 1):
                print(f"{i}. {config['name']}")

            try:
                choice = input("\nEnter number(s) to delete (comma-separated) or 'all', or press Enter to cancel: ")
                if choice.lower() == "all":
                    if input("Are you sure you want to delete ALL configurations? (y/N): ").lower() == "y":
                        for config in configs:
                            delete_endpoint_config(config["name"])
                elif choice.strip():
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    for idx in indices:
                        if 0 <= idx < len(configs):
                            delete_endpoint_config(configs[idx]["name"])
                        else:
                            print(f"Invalid index: {idx + 1}")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")


if __name__ == "__main__":
    main()
