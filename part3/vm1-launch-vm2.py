#!/usr/bin/env python3

import os

from google.cloud import compute_v1
from google.oauth2 import service_account

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
ZONE = "us-east1-d"
VM2_NAME = "lab5-vm2"

credentials = service_account.Credentials.from_service_account_file(
    "/srv/service-credentials.json"
)

instances_client = compute_v1.InstancesClient(credentials=credentials)


def wait_for_operation(operation):
    operation_client = compute_v1.ZoneOperationsClient(
        credentials=credentials
    )

    while True:
        result = operation_client.get(
            project=PROJECT,
            zone=ZONE,
            operation=operation.name,
        )

        if result.status == compute_v1.Operation.Status.DONE:
            if result.error:
                raise RuntimeError(result.error)
            return


def create_vm2():
    instance = compute_v1.Instance()
    instance.name = VM2_NAME
    instance.machine_type = f"zones/{ZONE}/machineTypes/f1-micro"

    disk = compute_v1.AttachedDisk()
    disk.boot = True
    disk.auto_delete = True

    disk.initialize_params = compute_v1.AttachedDiskInitializeParams(
        source_image="projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts",
        disk_size_gb=10,
        disk_type=f"zones/{ZONE}/diskTypes/pd-standard",
    )

    instance.disks = [disk]

    network_interface = compute_v1.NetworkInterface()
    network_interface.network = "global/networks/default"

    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    access_config.type_ = "ONE_TO_ONE_NAT"

    network_interface.access_configs = [access_config]
    instance.network_interfaces = [network_interface]
    instance.tags = compute_v1.Tags(items=["allow-5000"])

    with open("/srv/vm2-startup-script.sh") as f:
        startup_script = f.read()

    instance.metadata = compute_v1.Metadata(
        items=[
            compute_v1.Items(
                key="startup-script",
                value=startup_script,
            )
        ]
    )

    operation = instances_client.insert(
        project=PROJECT,
        zone=ZONE,
        instance_resource=instance,
    )

    wait_for_operation(operation)

    print(f"Created VM-2: {VM2_NAME}")


if __name__ == "__main__":
    create_vm2()
