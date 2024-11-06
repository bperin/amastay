import boto3
import argparse
from datetime import datetime


def list_endpoints(status_filter=None, verbose=True):
    """
    List all SageMaker endpoints with their details
    Args:
        status_filter (str, optional): Filter endpoints by status ('InService', 'Creating', etc.)
        verbose (bool): Whether to print the output
    Returns:
        list: List of endpoint details
    """
    sagemaker_client = boto3.client("sagemaker")
    endpoints = sagemaker_client.list_endpoints()["Endpoints"]

    if verbose:
        print("\n{:<40} {:<15} {:<20} {:<25}".format("Endpoint Name", "Status", "Instance Type", "Creation Time"))
        print("-" * 100)

    endpoint_details = []
    for endpoint in endpoints:
        desc = sagemaker_client.describe_endpoint(EndpointName=endpoint["EndpointName"])

        if status_filter and desc["EndpointStatus"] != status_filter:
            continue

        config = sagemaker_client.describe_endpoint_config(EndpointConfigName=desc["EndpointConfigName"])
        instance_type = config["ProductionVariants"][0]["InstanceType"]
        creation_time = desc["CreationTime"].strftime("%Y-%m-%d %H:%M:%S")

        if verbose:
            print("{:<40} {:<15} {:<20} {:<25}".format(desc["EndpointName"], desc["EndpointStatus"], instance_type, creation_time))

        endpoint_details.append({"name": desc["EndpointName"], "status": desc["EndpointStatus"], "instance_type": instance_type, "creation_time": creation_time})

    return endpoint_details


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


def cleanup_endpoint_resources(endpoint_name):
    """Clean up both endpoint and its configuration"""
    sagemaker_client = boto3.client("sagemaker")

    # First get the endpoint config name
    try:
        endpoint_desc = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        config_name = endpoint_desc["EndpointConfigName"]

        # Delete endpoint first
        delete_endpoint(endpoint_name)
        # Then delete config
        delete_endpoint_config(config_name)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


def delete_endpoint(endpoint_name):
    """Delete a specific endpoint and its configuration"""
    cleanup_endpoint_resources(endpoint_name)


def main():
    parser = argparse.ArgumentParser(description="Manage SageMaker endpoints")
    parser.add_argument("--list", action="store_true", help="List all endpoints")
    parser.add_argument("--status", choices=["InService", "Creating", "Failed"], help="Filter endpoints by status")
    parser.add_argument("--delete", action="store_true", help="Delete endpoints (will prompt for confirmation)")
    parser.add_argument("--endpoint", help="Specific endpoint name to delete")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    # List endpoints
    endpoints = list_endpoints(status_filter=args.status)

    # Handle deletion
    if args.delete:
        if args.endpoint:
            # Delete specific endpoint
            if input(f"\nConfirm deletion of endpoint '{args.endpoint}'? (y/N): ").lower() == "y":
                delete_endpoint(args.endpoint)
        else:
            # Show endpoints and ask which to delete
            print("\nAvailable endpoints for deletion:")
            for i, endpoint in enumerate(endpoints, 1):
                print(f"{i}. {endpoint['name']} ({endpoint['status']})")

            try:
                choice = input("\nEnter number(s) to delete (comma-separated) or 'all', or press Enter to cancel: ")
                if choice.lower() == "all":
                    if input("Are you sure you want to delete ALL endpoints? (y/N): ").lower() == "y":
                        for endpoint in endpoints:
                            delete_endpoint(endpoint["name"])
                elif choice.strip():
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    for idx in indices:
                        if 0 <= idx < len(endpoints):
                            delete_endpoint(endpoints[idx]["name"])
                        else:
                            print(f"Invalid index: {idx + 1}")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")


if __name__ == "__main__":
    main()
