# Images and Creds Scanning utility

This utility have two parts:-
- Images scanning utility :-<br/>
    In this utility of current version we can scan  the images present on the AWS ECR based on the images name and images versions provided in config as yaml.
- Credentials scanning utility :-<br/>
    In this utility of current version we can scan the credentails in public repositories and organisations like github/gitlab on basis of config provide as yaml.


## Prerequisite
- [Trivy Tool](https://github.com/aquasecurity/trivy)
- [AWS Configure](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)

## Config File
- Images Scanner
  ```
  ecr:
    aws_profile: profile_name
    region: region_name
    ecrurl: ecr_url_link         #Example -> 727357989976.dkr.ecr.us-east-1.amazonaws.com

    repos:
        - repo_name1             #mention repo_name here
        - repo_name2

    image_versions:
        - v1
        - v2
  ```
- Creds Scanner
  ```
    repositories:
        specs:
            plateforms:
                github:
                    users:
                        - public:user_name:repo                   #mode:user:repo
                        - public:user_name                        #no repo means will scan all repo

                    organisations:
                        - public:user_name:org_name:repo_name     #user:org:public:repo
                        - public:user_name:org_name

                gitlab:
                    users:
                        - public:user_name:repo                   #mode:user:repo
                        - public:user_name                        #no repo means will scan all repo

                    organisations:
                        - public:user_name:org_name:repo_name     #user:org:public:repo
                        - public:user_name:org_name
  ```
## Steps to run the utility on local
- Install [Trivy Tool](https://github.com/aquasecurity/trivy)
- Clone the repository [Repo](https://github.com/aquasecurity/trivy)
- Install all packages mention in the requirements.txt

- Images Scanner:-
    - Export config file as environment variable by following command <br/>
        ```
        export CONF_PATH="${pwd}/config/scan_images_sample_config.yml"
        ```
    - Run the utility via  following command<br/>
        ```
        python3 scripts/actions_images.py
        ```
- Credentials Scanner:-
    - Export config file as environment variable by following command <br/>
        ```
        export CONF_PATH="${pwd}/config/scan_creds_sample_config.yml"
        ```
    - Run the utility via  following command<br/>
        ```
        python3 scripts/scan_creds.py
        ```

## Output

- Images Scanner
    - HTML Report
- Credentials Scanner
    - HTML Report


## Upcoming
- Images Scanner
    - Multiple AWS account support
- Credentials Scanner
    - Private repository support
    - Sonarqube report format support
