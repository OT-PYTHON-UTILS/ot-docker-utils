# Images  Scanning utility

## Images scanning utility :-<br/>
This utility scans private AWS ECR images defined by user in config file. 


## Prerequisite
- [Docker](https://docs.docker.com/engine/install/)
- [Trivy Tool](https://github.com/aquasecurity/trivy)
- [AWS Configure](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)

## Config File
  ```
  ecr:
    aws_profiles:
        default:
            aws_regions:
                us-east-2:
                    repositories:
                    - repo:version
                    - repo:*

  ```
### Note:-
In the above config section we can mention the multiple aws_profiles, multiple regions and multiple repositories:

- For the mutilple aws_profile config file will be look like below:- 
```
ecr:
    aws_profiles:
        default:
            aws_regions:
                us-east-2:
                    repositories:
                    - repo:version
                    - repo:*
        opstree:
            aws_regions:
                us-east-1:
                    repositories:
                    - repo:version
                    - repo:*
```
- For the mutilple aws_regions config file will be look like below:-
```
ecr:
    aws_profiles:
        default:
            aws_regions:
                us-east-2:
                    repositories:
                    - repo:version
                    - repo:*
                us-east-1:
                    repositories:
                    - repo:version
                    - repo:*
```
- For the mutilple aws_regions config file will be look like below:- <br/>
Note:- <br/>
To scan the specfic version of the given image, mention like "repo:version" <br/>
To scan all the versions of given images mention like "repo:*"

```
ecr:
    aws_profiles:
        default:
            aws_regions:
                us-east-2:
                    repositories:
                    - repo:version
                    - repo:*
```

### Example 
#### Config file with mutiple aws_profiles, aws_regions and repostiories are :- 
```
ecr:
    aws_profiles:
        default:
            aws_regions:
                us-east-1:
                    repositories:
                    - repo:version
                    - repo:*
                us-east-2:
                    repositories:
                    - repo:version
                    - repo:*
        opstree:
            aws_regions:
                us-east-1:
                    repositories:
                    - repo:version
                    - repo:*
                us-east-2:
                    repositories:
                    - repo:version
                    - repo:*
```

## Steps to run the utility locally
- Install [Docker](https://docs.docker.com/engine/install/)
- Install [Trivy Tool](https://github.com/aquasecurity/trivy)
- Clone the repository(branch-> dev) [Repo](https://github.com/OT-PYTHON-UTILS/ot-docker-utils.git)
- Install all packages mention in the requirements.txt

- Export config file as environment variable by following command <br/>
    ```
    export CONF_PATH="${pwd}/config/image_scanner_sample_config.yml"
    ```
- Run the utility via  following command<br/>
    ```
    python3 scripts/scan_images.py
    ```
## Steps to run the utility via Docker

- Run the command to build the image by following command:
    ```

    make VERSION=1.0 CONF_PATH=${pwd}/config/image_scanner_sample_config.yml scan_images_build
    ```
- Run the docker images of above one created by following command:
    ```
    make VERSION=1.0 CONF_PATH=${pwd}/config/image_scanner_sample_config.yml scan_images_run
    ```

## Output
- Scanning Logs
![Scanning Logs Example](Images/scanning_logs.png)

- HTML Report
![Html Report Example](Images/html_report.png)


<br>


<br/>


# Cred  Scanning utility

## Cred scanning utility :-<br/>
In this utility of current version we can scan the public repositories of Github and GitLab on the basis of username, repository name and organisation name provided in config as yaml.


## Prerequisite
- [Docker](https://docs.docker.com/engine/install/)
- [Trivy Tool](https://github.com/aquasecurity/trivy)


## Config File
  ```
  repositories:
    specs:
        plateforms:
            github:
                users:
                    - public:Abkt2001:Jenkins       #public:user:repo
                    - public:AbktOps                #no repo means will scan all repo

                organisations:
                    - public:AbktOps:OT-TRAINING:spinnaker-study      #public:user:org:repo
                    - public:AbktOps:OT-TRAINING                      #no repo means will scan all repo

            gitlab:
                users:
                    - public:abhiGurukulam

                organisations:
  ```
### Note:-
In the above config section we can mention the multiple repositories in the two way:
1. <b>public:usern_name:repo</b> <br/>
    Here, In this format replace the user_name with your github or gitlab user_name and replace repo with your repository name which you want to scan.
2. <b>public:usern_name</b> <br/>
    Here, In this format replace the user_name with your github or gitlab user_name. It will scan all the public repository present in the given user_name.

### Example 
#### Config file with mutiple repostiories are :- 
```
repositories:
    specs:
        plateforms:
            github:
                users:
                    - public:Abkt2001:Jenkins       #mode:user:repo
                    - public:AbktOps                #no repo means will scan all repo

                organisations:
                    - public:AbktOps:OT-TRAINING:spinnaker-study      # - user:org:public/priv:repo
                    - public:AbktOps:OT-TRAINING

            gitlab:
                users:
                    - public:abhiGurukulam

                organisations:
```

## Steps to run the utility on locally
- Install [Docker](https://docs.docker.com/engine/install/)
- Install [Trivy Tool](https://github.com/aquasecurity/trivy)
- Clone the repository(branch-> creds_scanning) [Repo](https://github.com/OT-PYTHON-UTILS/ot-docker-utils.git)
- Install all packages mention in the requirements.txt

- Export config file as environment variable by following command <br/>
    ```
    export CONF_PATH="${pwd}/config/scan_creds_sample_config.yml"
    ```
- Run the utility via  following command<br/>
    ```
    python3 scripts/scan_creds.py
    ```

## Steps to run the utility via Docker
- Run the command to build the image by following command:
    ```
    make VERSION=1.0 CONF_PATH=${pwd}/config/scan_creds_sample_config.yml scan_creds_build
    ```
- Run the docker images of above one created by following command:
    ```
    make VERSION=1.0 CONF_PATH=${pwd}/config/image_scanner_sample_config.yml scan_creds_run
    ```
## Output
- Scanning Logs
![Scanning Logs Example](Images/creds_logs.png)

