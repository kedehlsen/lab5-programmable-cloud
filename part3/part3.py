#!/usr/bin/env python3

import os

from google.cloud import compute_v1
from google.oauth2 import service_account


PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "lab-5-510203")
ZONE = "us-east1-d"
VM1_NAME = "lab5-vm1"


def create_vm1():
    credentials = service_account.Credentials.from_service_account_file(
        "service-credentials.json"
    )

    instances_client = compute_v1.InstancesClient(credentials=credentials)

    instance = compute_v1.Instance()
    instance.name = VM1_NAME
    instance.machine_type = f"zones/{ZONE}/machineTypes/f1-micro"

    # Boot disk for VM-1
    disk = compute_v1.AttachedDisk()
    disk.boot = True
    disk.auto_delete = True
    disk.initialize_params = compute_v1.AttachedDiskInitializeParams(
        source_image=(
            "projects/ubuntu-os-cloud/global/images/"
            "family/ubuntu-2204-lts"
        ),
        disk_size_gb=10,
        disk_type=f"zones/{ZONE}/diskTypes/pd-standard",
    )
    instance.disks = [disk]

    # Network + external IP
    network_interface = compute_v1.NetworkInterface()
    network_interface.network = "global/networks/default"

    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    access_config.type_ = "ONE_TO_ONE_NAT"

    network_interface.access_configs = [access_config]
    instance.network_interfaces = [network_interface]

    # Read the files that VM-1 needs.
    with open("vm1-launch-vm2.py") as f:
        launch_code = f.read()

    with open("vm1-startup-script.sh") as f:
        vm1_startup = f.read()

    with open("vm2-startup-script.sh") as f:
        vm2_startup = f.read()

    with open("service-credentials.json") as f:
        service_credentials = f.read()

    # Pass the files to VM-1 through instance metadata.
    instance.metadata = compute_v1.Metadata(
        items=[
            compute_v1.Items(
                key="startup-script",
                value=vm1_startup,
            ),
            compute_v1.Items(
                key="vm1-launch-vm2-code",
                value=launch_code,
            ),
            compute_v1.Items(
                key="vm2-startup-script",
                value=vm2_startup,
            ),
            compute_v1.Items(
                key="service-credentials",
                value=service_credentials,
            ),
            compute_v1.Items(
                key="project",
                value=PROJECT,
            ),
        ]
    )

    print(f"Creating VM-1 ({VM1_NAME}) in {ZONE}...")

    operation = instances_client.insert(
        project=PROJECT,
        zone=ZONE,
        instance_resource=instance,
    )

    operation.result()

    print(f"VM-1 ({VM1_NAME}) created.")


if __name__ == "__main__":
    create_vm1()
