# license_returner

The license_returner component returns any IDL licenses that were used in the current execution of the Generate workflow. It determines license usage via a unique identifier.

Top-level Generate repo: https://github.com/podaac/generate

## pre-requisites to building

None

## build command

`docker build --tag license:0.1 . `

## execute command

Arguments:
1. unique_id: Integer to identify IDL licenses used by workflow in Parameter Store.
2. prefix: String Prefix for environment that Generate is executing in.
3. dataset: Name of dataset that has been processed.
4. processing_type: Either `quicklook` or `refined`. Used to return licenses reserved for these particular job types.

MODIS A: 
`docker run --name returner --rm -e AWS_ACCESS_KEY_ID=$aws_key -e AWS_SECRET_ACCESS_KEY=$aws_secret -e AWS_DEFAULT_REGION=$default_region returner:latest 6233 podaac-sndbx-generate aqua quicklook`

MODIS T: 
`docker run --name returner --rm -e AWS_ACCESS_KEY_ID=$aws_key -e AWS_SECRET_ACCESS_KEY=$aws_secret -e AWS_DEFAULT_REGION=$default_region returner:latest 6233 podaac-sndbx-generate terra refined`

VIIRS: 
`docker run --name returner --rm -e AWS_ACCESS_KEY_ID=$aws_key -e AWS_SECRET_ACCESS_KEY=$aws_secret -e AWS_DEFAULT_REGION=$default_region returner:latest 6233 podaac-sndbx-generate viirs quicklook`

## aws infrastructure

The downloader includes the following AWS services:
- AWS SSM Parameter Store

## terraform 

Deploys AWS infrastructure and stores state in an S3 backend using a DynamoDB table for locking.

To deploy:
1. Edit `terraform.tfvars` for environment to deploy to.
2. Edit `terraform_conf/backed-{prefix}.conf` for environment deploy.
3. Initialize terraform: `terraform init -backend-config=terraform_conf/backend-{prefix}.conf`
4. Plan terraform modifications: `terraform plan -out=tfplan`
5. Apply terraform modifications: `terraform apply tfplan`

`{prefix}` is the account or environment name.