#!/usr/bin/env bash

cd /autograder/source

apt-get install -y python3 python3-pip python-is-python3

mkdir -p /root/.ssh
cp ssh_config /root/.ssh/config
# Make sure to include your private key here
cp deploy_key /root/.ssh/deploy_key
# To prevent host key verification errors at runtime
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Clone autograder files
git clone git@github.com:hkn-mu/decal-attend.git /autograder/autograder_samples

# Checkout the right repository
cd /autograder/autograder_samples
git checkout sp25

# Install python dependencies
pip install -r /autograder/autograder_samples/requirements.txt
