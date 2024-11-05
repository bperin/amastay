#!/usr/bin/env python3

import boto3
import argparse
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger


def delete_endpoints():
    sagemaker = boto3.client("sagemaker")
    deleted = 0

    print("Deleting endpoints...")
    paginator = sagemaker.get_paginator("list_endpoints")
    for page in paginator.paginate():
        for endpoint in page["Endpoints"]:
            endpoint_name = endpoint["EndpointName"]
            try:
                print(f"Deleting endpoint: {endpoint_name}")
                sagemaker.delete_endpoint(EndpointName=endpoint_name)
                deleted += 1
            except Exception as e:
                print(f"Error deleting endpoint {endpoint_name}: {str(e)}")
    return deleted


def delete_endpoint_configs():
    sagemaker = boto3.client("sagemaker")
    deleted = 0

    print("Deleting endpoint configurations...")
    paginator = sagemaker.get_paginator("list_endpoint_configs")
    for page in paginator.paginate():
        for config in page["EndpointConfigs"]:
            config_name = config["EndpointConfigName"]
            try:
                print(f"Deleting endpoint configuration: {config_name}")
                sagemaker.delete_endpoint_config(EndpointConfigName=config_name)
                deleted += 1
            except Exception as e:
                print(f"Error deleting config {config_name}: {str(e)}")
    return deleted


def cleanup_job(endpoints=False, configs=False, all=False):
    if all or endpoints:
        deleted = delete_endpoints()
        print(f"Deleted {deleted} endpoints")

    if all or configs:
        deleted = delete_endpoint_configs()
        print(f"Deleted {deleted} endpoint configurations")


def main():
    parser = argparse.ArgumentParser(description="Delete SageMaker endpoints and configurations")
    parser.add_argument("--endpoints", action="store_true", help="Delete endpoints")
    parser.add_argument("--configs", action="store_true", help="Delete endpoint configurations")
    parser.add_argument("--all", action="store_true", help="Delete both endpoints and configurations")
    parser.add_argument("--interval", type=int, help="Run every N seconds", default=3600)

    args = parser.parse_args()

    if not (args.endpoints or args.configs or args.all):
        parser.print_help()
        sys.exit(1)

    scheduler = BlockingScheduler()
    scheduler.add_job(cleanup_job, trigger=IntervalTrigger(seconds=args.interval), args=[args.endpoints, args.configs, args.all])

    try:
        print(f"Starting scheduler, will run every {args.interval} seconds")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
