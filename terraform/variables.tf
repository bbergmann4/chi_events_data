variable "CREDENTIALS" {
  description = "Google Cloud Service Account Credentials:  Resource Admin"
  default     = "<Path to your Service Account json file>"
  #This will be overidden if you created TF_VAR_credentials.  If you'd rather use a local file 
  #ex: if you have a directory where this file is called keys with your service account json file
  #saved there as my-creds.json you could use default = "./keys/my-creds.json"
  #be sure to add any credential files to your gitignore.  
}


variable "PROJECTID" {
  description = "Project"
  default     = "your-projectid-01234"
  #Will use the codespace secret or you can update here reflect the GCP project id for your credentials
}

variable "region" {
  description = "Region"
  #Update the below if it differs from your region
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  #Update the below if it differs from your location
  default     = "US"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  #You do not need to update the default name
  default     = "chi_events"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  #Update the below to make a unique bucket name.  Ex: Add your project id or date.
  default     = "chi-events-0328"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}