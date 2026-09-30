#!/bin/bash

set -e

apt-get update
apt-get install -y python3 python3-pip curl

mkdir -p /srv
cd /srv

curl -H "Metadata-Flavor: Google" \
  http://metadata/computeMetadata/v1/instance/attributes/vm1-launch-vm2-code \
  -o vm1-launch-vm2.py

curl -H "Metadata-Flavor: Google" \
  http://metadata/computeMetadata/v1/instance/attributes/vm2-startup-script \
  -o vm2-startup-script.sh

curl -H "Metadata-Flavor: Google" \
  http://metadata/computeMetadata/v1/instance/attributes/service-credentials \
  -o service-credentials.json

export GOOGLE_CLOUD_PROJECT=$(curl -s \
  -H "Metadata-Flavor: Google" \
  http://metadata/computeMetadata/v1/project/project-id)

pip3 install --upgrade google-cloud-compute

python3 /srv/vm1-launch-vm2.py
