
from otawslibs import generate_aws_session
import sys, os, argparse, logging, yaml, json, json_log_formatter, pathlib, boto3

from botocore.exceptions import ClientError

SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.insert(1, f'{SCRIPT_PATH}/./ot-filesystem-libs/otfilesystemlibs')
sys.path.insert(2, f'{SCRIPT_PATH}/../ot-aws-libs/otawslibs/')

import images_action_factory

from otfilesystemlibs import yaml_manager


CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/ot/aws-resource-scheduler.log"


FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


def _scheduleFactory(properties, args):

    try:

        client = boto3.client('ecr')
        imageScansActions = images_action_factory.imageScansActions(client)
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
                    LOGGER.info( f'Scanning ECR images resources in {region} region based on provided image versions tags {image_versions}')
                    image_repos = imageScansActions._list_imageVersion_repos(image_versions)
                    imageScansActions._scan_imageVersion_repos(image_repos)

                if remote_repository:
                    LOGGER.info(
                        f'Found remote repository details for image scanning : {remote_repository}')
                    for repo in remote_repository:
                        LOGGER.info( f'Scanning ECR images resources in {region} region based on provided repository  {repo}')
                        images = imageScansActions._get_images(repo)
                        imageScansActions._scan_images(images, repo)
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
    
    yaml_managers = yaml_manager.getYamlLoader()
    properties = yaml_managers._loadYaml(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')


    _scheduleFactory(properties, args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file",
                        default=os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _scheduleResources(args)
