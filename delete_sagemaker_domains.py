#!/usr/bin/env python3

import boto3
import argparse
import sys
import time


def delete_domains():
    sagemaker = boto3.client("sagemaker")
    deleted = 0

    print("Deleting domains...")
    paginator = sagemaker.get_paginator("list_domains")
    for page in paginator.paginate():
        for domain in page["Domains"]:
            domain_id = domain["DomainId"]
            try:
                print(f"Deleting domain: {domain_id}")

                # First, list and delete all apps for each user profile
                user_paginator = sagemaker.get_paginator("list_user_profiles")
                for user_page in user_paginator.paginate(DomainIdEquals=domain_id):
                    for user in user_page["UserProfiles"]:
                        user_name = user["UserProfileName"]
                        print(f"  Processing user profile: {user_name}")

                        # Delete all apps for this user
                        app_paginator = sagemaker.get_paginator("list_apps")
                        for app_page in app_paginator.paginate(DomainIdEquals=domain_id, UserProfileNameEquals=user_name):
                            for app in app_page["Apps"]:
                                app_name = app["AppName"]
                                app_type = app["AppType"]
                                print(f"    Deleting app: {app_name} ({app_type})")
                                sagemaker.delete_app(DomainId=domain_id, UserProfileName=user_name, AppType=app_type, AppName=app_name)

                                # Wait for app deletion
                                print(f"    Waiting for app {app_name} to be deleted...")
                                waiter = sagemaker.get_waiter("app_deleted")
                                waiter.wait(DomainId=domain_id, UserProfileName=user_name, AppType=app_type, AppName=app_name)

                        # Now delete the user profile
                        print(f"  Deleting user profile: {user_name}")
                        sagemaker.delete_user_profile(DomainId=domain_id, UserProfileName=user_name)

                        # Wait for user profile deletion
                        print(f"  Waiting for user profile {user_name} to be deleted...")
                        waiter = sagemaker.get_waiter("user_profile_deleted")
                        waiter.wait(DomainId=domain_id, UserProfileName=user_name)

                # Finally delete the domain
                print(f"Deleting domain {domain_id}...")
                sagemaker.delete_domain(DomainId=domain_id, RetentionPolicy={"HomeEfsFileSystem": "Delete"})
                deleted += 1

                # Wait for domain deletion
                print(f"Waiting for domain {domain_id} to be deleted...")
                waiter = sagemaker.get_waiter("domain_deleted")
                waiter.wait(DomainId=domain_id)

            except Exception as e:
                print(f"Error deleting domain {domain_id}: {str(e)}")
    return deleted


def main():
    parser = argparse.ArgumentParser(description="Delete SageMaker domains")
    parser.add_argument("--force", action="store_true", help="Delete without confirmation")

    args = parser.parse_args()

    if not args.force:
        confirm = input("Are you sure you want to delete all SageMaker domains? This cannot be undone. (y/N): ")
        if confirm.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    deleted = delete_domains()
    print(f"Deleted {deleted} domains")


if __name__ == "__main__":
    main()
