try:
    import configparser
except:
    from six.moves import configparser
import sys
import os
import argparse
import logging
import yaml
import json
import re
import json_log_formatter
import boto3
from botocore.exceptions import ClientError
from otawslibs import generate_aws_session
from otscannerlibs import scan_images_factory
from otfilesystemlibs import yaml_manager

CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/var/log/ot/scans_images.log"


FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


def _scanfactory(properties, args):

    try:

        for property in properties:

            if property == "ecr":

                for profile in properties['ecr']['aws_profiles']:

                    aws_regions = properties['ecr']['aws_profiles'][profile]['aws_regions']

                    for aws_region in aws_regions:

                        LOGGER.info(f'Connecting to AWS.')
                        session = generate_aws_session._create_session(profile)
                        client = session.client('ecr',region_name=aws_region)
                        scanImages = scan_images_factory.scanImages(client)

                        LOGGER.info(f'Connection to AWS established with profile {profile}.')

                        LOGGER.info(f'Reading ecr config for the profile {profile}')
                        try:
                            aws_account = session.client('sts').get_caller_identity()['Account']
                        except ClientError as e:
                            if "InvalidClientTokenId" in str(e):
                                logging.error(f"Invalid aws profile {profile} found. Error message: {e}")
                            else:
                                logging.error(f"{e}")
                            break

                        ecr_url = aws_account+".dkr.ecr."+aws_region+".amazonaws.com"
                        ecr_repositories = properties['ecr']['aws_profiles'][profile]['aws_regions'][aws_region]['repositories']

                        if ecr_repositories:
                            LOGGER.info(
                                f'Found ecr_repositories details for image scanning : {ecr_repositories}')

                            for repository in ecr_repositories:
                                fetched_repository_versions = re.split(
                                    '[:]', repository)
                                LOGGER.info(
                                    f'Scanning ecr_repositories in {aws_region} region based on provided repository  {repository}')

                                if fetched_repository_versions[1] == "*":
                                    repository_name = fetched_repository_versions[0]
                                    LOGGER.info(
                                    f'Scanning all versions of {repository_name} ecr-repository in {aws_region} region')

                                    scanImages._scan_images_with_all_versions(
                                        ecr_url, repository_name)

                                else:
                                    fetched_repository_versions[1] = list(
                                        fetched_repository_versions[1].split(","))
                                    repository_versions = fetched_repository_versions[1]
                                    repository_name = fetched_repository_versions[0]

                                    LOGGER.info(
                                    f'Scanning the versions {repository_versions} of {repository_name} ecr-repository in {aws_region} region')
                                    scanImages._scan_images_with_given_versions(
                                        ecr_url, repository_name, repository_versions)
                        else:
                            LOGGER.warning(
                                f'Found ecr section in config file but no repository  details mentioned for image scanning')
            else:
                LOGGER.info("Scanning AWS service details in config")

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure!!!! .. Please mention valid AWS profile in property file or use valid IAM role ').with_traceback(
                e.__traceback__)
        else:
            raise e


def _scanimages(args):

    LOGGER.info(
        f'Fetching properties from conf file: {args.property_file_path}.')

    yaml_managers = yaml_manager.getYamlLoader()
    properties = yaml_managers._loadYaml(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')

    _scanfactory(properties, args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file",
                        default=os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _scanimages(args)
