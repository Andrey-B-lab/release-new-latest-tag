import boto3
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)
import json

#activate Harbor replication function
def activate_harbor_replication(id):
    headers = {
                'accept': 'application/json',
                    'authorization': get_octopusvariable("harbor_authorization_stg"),
                        # Already added when you pass json= but not when you pass data=
                            # 'Content-Type': 'application/json',
                            }

    json_data = {
                'policy_id': id,
                }

    response = requests.post('https://registry.harbor.co.il/api/v2.0/replication/executions', headers=headers, json=json_data)

    # Note: json_data will not be serialized by requests
    # exactly as it was in the original request.
    #data = '{ "policy_id": id}'
    #response = requests.post('https://registry.harbor.co.il/api/v2.0/replication/executions', headers=headers, data=data)

### get staging tag ECR image sha (image digest)
def get_ecr_staging_sha(ecr_repo_name):
    client = boto3.client('ecr', region_name=get_octopusvariable("aws_region_name_stg"), aws_access_key_id= get_octopusvariable("aws_access_key_id_stg"), aws_secret_access_key= get_octopusvariable("aws_secret_access_key_stg"))
    response = client.describe_images(
            registryId=get_octopusvariable("aws_registry_id_stg"),
            repositoryName=ecr_repo_name,
            imageIds=[
                {
                 'imageTag': 'staging'
                },
            ],
            filter={
                'tagStatus': 'TAGGED'
                }
            )
    ecr_staging_sha = (response['imageDetails'][0]['imageDigest'])
    return(ecr_staging_sha)

### get staging tag Harbor image sha (image digest)
def get_harbor_staging_sha(harbor_repo_name):
    headers = {
        'accept': 'application/json',
        'X-Accept-Vulnerabilities': 'application/vnd.security.vulnerability.report; version=1.1, application/vnd.scanner.adapter.vuln.report.harbor+json; version=1.0',
        'authorization': get_octopusvariable("harbor_authorization_stg"),
    }

    params = {
        'page': '1',
        'page_size': '10',
        'with_tag': 'true',
        'with_label': 'false',
        'with_scan_overview': 'false',
        'with_signature': 'false',
        'with_immutable_status': 'false',
    }
    harbor_response = requests.get('https://registry.harbor.co.il/api/v2.0/projects/stg/repositories/' + harbor_repo_name + '/artifacts/staging', params=params, headers=headers)
    data = harbor_response.json()
    harbor_latest_sha = data.get("digest")
    return(harbor_latest_sha)

#Harbor  STG replications numbers
job_numbers = {'my-app-admin-api': 15,
        'my-app-admin-client': 16,
        'my-app-client': 31,
        'my-app-server': 30,
        'service-request-throttle': 11,
        'finavo-digifi': 26,
        'website-gateway-api': 8,
        'website-validation-service': 9,
        'websitep-bff': 43,
        'website-client': 5,
        'website-notification-service': 2,
        'website-user-management-api': 10,
        'website-payment-service': 37,
        'test-octopus-deploy': 38}

# If HARBOR sha and ECR sha are different, activate replication and proceed to the next Octopus runbook step
for name, job_number in job_numbers.items():
    if get_ecr_staging_sha(get_octopusvariable("Octopus.Project.Name")) != get_harbor_staging_sha(get_octopusvariable("Octopus.Project.Name")):
        activate_harbor_replication(job_number)
    else:
    	get_octopusvariable("Octopus.Step.Status.Error") # If HARBOR sha and ECR sha are the same, fail the current step so the procces will not proceed to the second step
