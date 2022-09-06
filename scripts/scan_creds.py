import argparse
import logging
import os
import sys
import json_log_formatter
from otfilesystemlibs import yaml_manager
from otscannerlibs import creds_action_factory

CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/var/log/ot/creds-scanner.log"

FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)

def _scanFactory(properties, args):

    try:
        for property in properties:
            LOGGER.info(f"Start to fetching the config file")
            if property == "repositories":
                CredScanningAction = creds_action_factory.CredScanningActions()
                LOGGER.info(f"Start fetching the plateforms")
                for plateform in properties['repositories']['specs']['plateforms']:
                    if plateform == "github":
                        LOGGER.info(f"Start to fetching the github spec")
                        try:
                            for repo in properties['repositories']['specs']['plateforms']['github']:
                                if repo!="users" and repo!="organisations":
                                    LOGGER.warning("Mention the repository(users,organisations) you want to scan ")
                                else:
                                    if repo=="users":
                                        github_users = properties['repositories']['specs']['plateforms']['github']['users']
                                        LOGGER.info(f"Fetched github users data are : {github_users}")
                                        CredScanningAction._scan_users_repo(github_users,plateform)

                                    if repo=="organisations":
                                        github_orgs = properties['repositories']['specs']['plateforms']['github']['organisations']
                                        LOGGER.info(f"Fetched github orgs data are : {github_orgs}")
                                        CredScanningAction._scan_org_repo(github_orgs,plateform)
                        except TypeError as e:
                            if "NoneType" in str(e):
                                LOGGER.warn("Github section is empty no users and orgs section")

                    if plateform == "gitlab":
                        LOGGER.info(f"Start to fetching the plateform gitlab spec")
                        try:
                            for repos in properties['repositories']['specs']['plateforms']['gitlab']:
                                if repos!="users" and repos!="organisations":
                                    LOGGER.warning("Mention the repository(users,organisations) you want to scan ")
                                else:
                                    if repos=="users":
                                        gitlab_users = properties['repositories']['specs']['plateforms']['gitlab']['users']
                                        LOGGER.info(f"Fetched gitlab users data are : {gitlab_users}")
                                        CredScanningAction._scan_users_repo(gitlab_users,plateform)
                                    if repos=="organisations":
                                        gitlab_orgs = properties['repositories']['specs']['plateforms']['gitlab']['organisations']
                                        LOGGER.info(f"Fetched gitlab orgs data are : {gitlab_orgs}")
                                        CredScanningAction._scan_org_repo(gitlab_orgs,plateform)
                        except TypeError as e:
                            if "NoneType" in str(e):
                                LOGGER.warning("GitLab section is empty no users and orgs section")        
            else:
                LOGGER.error(f'Wrong format of the config file')



    except TypeError as e:
        if "NoneType" in str(e):
            raise Exception('Config file is empty, enter the valid data in the config file ').with_traceback(
                e.__traceback__)
        else:
            raise e


def _scanResources(args):

    LOGGER.info(
        f'Fetching properties from conf file: {args.property_file_path}.')

    yaml_managers = yaml_manager.getYamlLoader()
    properties = yaml_managers._loadYaml(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')

    _scanFactory(properties, args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file",
                        default=os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _scanResources(args)
