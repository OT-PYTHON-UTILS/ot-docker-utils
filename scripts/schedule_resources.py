
from otawslibs import generate_aws_session
import sys, os, argparse, logging, yaml, json, json_log_formatter, pathlib, boto3

from botocore.exceptions import ClientError

SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.insert(1, f'{SCRIPT_PATH}/../lib')

import load_yaml_config

CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/tmp/ot/aws-resource-scheduler.log"


FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


def _get_images(client, repository):
    images_details = client.describe_images(repositoryName=repository)
    images = []
    for imgdetails in range(len(images_details['imageDetails'])):
        for image in images_details['imageDetails'][imgdetails]['imageTags']:
            images.append(image)
    return(images)


def _get_all_repositories(client):
    repositories = []
    get_repositories = client.describe_repositories()
    for repository in range(len(get_repositories)):
        repositories.append(
            get_repositories['repositories'][repository]['repositoryName'])
    return repositories



def _scan_images(client, images, repository):
    for image in images:
            command = f"trivy image --format template --template '@trivy/contrib/html.tpl' -o reports/{image}.html 727357989976.dkr.ecr.us-east-1.amazonaws.com/{repository}:{image}"
            print(
                f"trivy image --format template --template '@trivy/contrib/html.tpl' -o reports/{image}.html 727357989976.dkr.ecr.us-east-1.amazonaws.com/{repository}:{image}")
            os.system(command)

#   will list the images with repository having the image_version pass in the config
def _list_imageVersion_repos(client, image_versions):
    images_repo = {}
    repositories = _get_all_repositories(client)
    for repository in repositories:
        image = client.list_images(repositoryName=repository)
        image_ids = image['imageIds']
        for image_version in image_versions:
            for image_id in range(len(image_ids)):
                if image['imageIds'][image_id]['imageTag'] == image_version :
                    images_repo.update({repository : image['imageIds'][image_id]['imageTag']})

    return images_repo

def _scan_imageVersion_repos(client, image_repos):
    for repo,image in image_repos.items():
        command = f"trivy image --format template --template '@trivy/contrib/html.tpl' -o reports/{repo}-{image}.html 727357989976.dkr.ecr.us-east-1.amazonaws.com/{repo}:{image}"
        os.system(command)

def _scheduleFactory(properties, args):

    try:

        client = boto3.client('ecr')
        for property in properties:

            if property == "ECR":

                LOGGER.info(f'Connecting to AWS.')

                if properties['ECR']['aws_profile']:
                    session = generate_aws_session._create_session(
                        properties['ECR']['aws_profile'])
                else:
                    session = generate_aws_session._create_session()

                LOGGER.info(f'Connection to AWS established.')

                LOGGER.info(f'Reading ECR config')

                remote_repository = properties['ECR']['repo']
                image_versions = properties['ECR']['image_versions']
                region = properties['ECR']["region"]

                if image_versions:

                    LOGGER.info(
                        f'Found image tags details for image scanning : {image_versions}')
                    client = boto3.client('ecr')
                    LOGGER.info( f'Scanning ECR images resources in {region} region based on provided image versions tags {image_versions}')
                    image_repos =_list_imageVersion_repos(client, image_versions)
                    _scan_imageVersion_repos(client, image_repos)

                if remote_repository:
                    LOGGER.info(
                        f'Found remote repository details for image scanning : {remote_repository}')
                    client = boto3.client('ecr')
                    for repo in remote_repository:
                        LOGGER.info( f'Scanning ECR images resources in {region} region based on provided repository  {repo}')
                        images = _get_images(client, repo)
                        _scan_images(client, images, repo)
                else:
                    LOGGER.warning(
                        f'Found ECR section in config file but no repository  details mentioned for image scanning')
            else:
                LOGGER.info("Scanning AWS service details in config")

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure!!!! .. Please mention valid AWS profile in property file or use valid IAM role ').with_traceback(
                e.__traceback__)
        else:
            raise e


def _scheduleResources(args):

    LOGGER.info(
        f'Fetching properties from conf file: {args.property_file_path}.')

    properties = load_yaml_config._getProperty(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')


    _scheduleFactory(properties, args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file",
                        default=os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _scheduleResources(args)
