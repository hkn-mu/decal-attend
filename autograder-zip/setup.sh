#!/usr/bin/env bash

cd /autograder/source

apt-get install -y python python-pip python-dev

mkdir -p /root/.ssh
cp ssh_config /root/.ssh/config
# Make sure to include your private key here
cp deploy_key /root/.ssh/deploy_key
# To prevent host key verification errors at runtime
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Copy Google service account key
cp secret.json /autograder/autograder_samples/secret.json

# Clone autograder files
git clone git@github.com:hkn-mu/decal-attend.git /autograder/autograder_samples

# Checkout the right repository
cd /autograder/autograder_samples
git checkout gapi-test

# Install python dependencies
pip install -r /autograder/autograder_samples/requirements.txt