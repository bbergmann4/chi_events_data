#!/bin/bash

# terraform
#Update wget if you are not using linux:  https://developer.hashicorp.com/terraform/install
wget https://releases.hashicorp.com/terraform/1.14.8/terraform_1.14.8_linux_amd64.zip
sudo unzip terraform_1.14.8_linux_amd64.zip -d /usr/bin
rm terraform_1.14.8_linux_amd64.zip