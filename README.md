# chi_events_data
Data Engineering Zoomcamp 2026 Project

[TOC]

# The Problem
This workflow aims to build a pipeline from the City of Chicago’s data portal to a GCP data warehouse and dashboard. The City of Chicago provides multiple lists of events authorized by city departments, including park district events at parks and library system events at libraries. The pipeline will normalize and consolidate these two sources and join them with location information.
## Project Goals
- Create an end-to-end ETL process ending with a simple report
- Make it replicable with easy-to-follow documentation
- Explore the Chicago Data Portal
## Tools & Approach
In order to accomplish these goals, I plan to use the following tools:
- Github codespaces as an easy replicable virtual environment 
- Provision infrastructure as code using Terraform
- Orchestrate ETL and testing with Bruin
- Create Python environment in uv for replicable package management 
- Utilize GCP buckets, BigQuery, and Google Looker for storage, analysis, and reporting
- The workflow was  built in Github Codespaces, using codespace secrets for a clean environment and replicability

# The Data

## Chicago Data Portal

The City of Chicago maintains a large library of public datasets in a variety of formats.  Many of these are accessible through their SODA3 API.  

[Library Events Metadata](https://data.cityofchicago.org/Events/Chicago-Public-Library-Events/vsdy-d8k7/about_data)

[Library Locations Metadata](https://data.cityofchicago.org/Education/Libraries-Locations-Contact-Information-and-Usual-/x8fc-8rcq/about_data)

[Park Events Metadata](https://data.cityofchicago.org/Events/Chicago-Park-District-Event-Permits/pk66-w54g/about_data)

[Park District Facilities Locations Metadata](https://data.cityofchicago.org/Parks-Recreation/CPD_Facilities/eix4-gf83/about_data)


## Data Formats


# Project Evaluation

Feel free to create a fork of this repository or use github importer to make a disconnected copy in your github.  I've built this so that you can easily replicate this workflow the Github Codespaces. If you follow this path, all of the tools needed will be installed using the .devcontainer.json file and you will provide all credentials needed through codespace secrets.  

It is possible to run this process "in production" on a standalone virtual machine with minimal changes.  Instead of storing secrets in github, you would store them as environment variables.  Tools can be installed with the setup.sh file provided (run run `bash setup.sh` ).   

Before getting started, you will need to have your own google cloud platform account. The files are of trivial size and it is not a highly computational process, so any expense should be minimal.  You will also be required to provide information to sign up for a free API account with the City of Chicago (described below)

## Credentials

### Google Cloud Platform

You will need to create service account credentials by following the instructions [here](https://developers.google.com/workspace/guides/create-credentials).  

These instructions call for creating two service accounts.  The first is a resouce admin that will be used to provision the initial build of the project.  The second is an ETL account with more limited permissions.  For optimal security, you can disable the admin acount after you initialize the project and add resource specific IAM conditions to the ETL account.  Alternatively, for easy setup, you can re-use the resource admin account information for both use cases.  

 A Resource Admin Service Account:  
 - roles/storage.admin
 - roles/bigquery.admin

An ETL Service Account
 - roles/storage.objectAdmin (bucket level after creation)
 - roles/bigquery.dataEditor (dataset level)
 - roles/bigquery.jobUser (project leve)
 - roles/bigquery.dataViewer (dataset level)

### Chicago Data Portal API

In order to call the API, you will need to have an api key. You can do this by visiting the [developer page](https://data.cityofchicago.org/profile/edit/developer_settings). 

1. Click create new account at the bottom and fill out your account information 
2. When requested, verify your address and [sign in](https://data.cityofchicago.org/login )
3. Now, your username will appear on the top right.  Click on your username drop down and go to [Developer Settings](https://data.cityofchicago.org/profile/edit/developer_settings)
4.  Now you should see a button to create a new API key.  Copy the secret in a safe place for now so that you can save it in to github secrets.

### Storing Credentials

In order to safely store secrets in this project, I am using codespace secrets that act as environment variables within the VM.
1.  Login to github in your browswer, open your copy of this repo, and go to settings
2.  Under  Security there is "Secrets and variables" header.  Click on Codespaces.
3.  Create the following 5 codespace secrets in this repo:

 **Your GCP credentials**

 ETL Account
  - Name:  GCP_ETL_CRED
  - Secret:  _The contents of your ETL service account json_

Resource Admin Account
  - Name TF_VAR_CREDENTIALS
  - Secret:  _The contents of your resource admin service account json_

Project ID
  - Name:  TF_VAR_PROJECTID
  - Secret:  _The project id associated with the above service accounts (looks like random-word-1234-a2)_

**Your Chicago Data Portal credenials**

  - Name:  CHI_API_ID
  - Secret:  _The API Key ID provided by data.cityofchicago.org_

  
  - Name:  CHI_API_SECRET
  - Secret:  _The API Key Secret provided by data.cityofchicago.org_

## Terraform

This process will create a google cloud storage bucket and a BigQuery dataset for this project.  Be aware that these tools will incur a cost.  

### Setup

Terraform will allow you to provision the GCP resources you need for this project.  However, you may need to update the variables.tf file to reflect your own configuration.

 - Create a unique name for your storage bucket
 - Update the region (default=us-central1) and location (us) if they do not reflect your GCP setup
 - If you aren't using codespace secrets, you can provide path to credentials

 Alternatively, you can overide my default values with the following syntax:
```
terraform plan -var="gcs_bucket_name=<a-unique-bucket>"
terraform apply  -var="gcs_bucket_name=<a-unique-bucket>"
```

### Execution

Change your working directory to the terraform directory.  

Then, initialize terraform
```
terraform init
```
Run, plan and check the result. 
```
terraform plan
```
Then, execute the build and create the resources
```
terraform apply
```
When you are done with these resources, you can pull them down with `terraform destroy`.  This will delete all data in your dataset. Be aware that your tfstate files are in the gitignore and will not be included when you push to repo.  When you are done, return to the root directory.


## Bruin Chi-Data Pipeline

Bruin CLI install is part of the devcontainer.json as well as the setup.sh process.  You may want to add the Bruin vscode extension for visibility.  A .bruin.yml file is included and is populated with the github secrets.  


## Tests

## Analysis