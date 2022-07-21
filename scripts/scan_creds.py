import argparse, re , requests
from giturlparse import parse
import logging
import os
import sys
import json_log_formatter
from botocore.exceptions import ClientError
from otfilesystemlibs import yaml_manager

CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/tmp/ot/creds-scanner.log"

FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)



def _fetch_github_repo_urls(user):
    urls = []
    data = re.split('[:]',user)
    if data[0] == "public":
        if len(re.split('[:]',user)) == 3:
            github_username = data[1]
            github_repo = data[2]
            URL =  "https://github.com/"+github_username+"/"+github_repo+".git"
            urls.append(URL)

        if len(re.split('[:]',user)) == 2:
            data = re.split('[:]',user)
            github_username = data[1]
            URL = "https://api.github.com/users/"+github_username+"/repos"
            response = requests.get(url = URL)
            for x in range(len(response.json())):
                urls.append(response.json()[x]["clone_url"])

    if data[0] == "private":
        pass

    return urls


def _fetch_gitlab_repo_urls(user):
    urls = []
    data = re.split('[:]',user)
    if data[0] == "public":
        if len(re.split('[:]',user)) == 3:
            gitlab_username = data[1]
            gitlab_repo = data[2]
            URL = "https://gitlab.com/"+gitlab_username+"/"+gitlab_repo+".git"
            urls.append(URL)

        if len(re.split('[:]',user)) == 2:
            data = re.split('[:]',user)
            gitlab_username = data[1]
            URL = "https://gitlab.com/api/v4/users/"+gitlab_username+"/projects/"
            response = requests.get(url = URL)
            for x in range(len(response.json())):
                urls.append(response.json()[x]['http_url_to_repo'])

    if data[0] == "private":
        pass

    return urls


def _fetch_github_org_urls(org):
    urls = []
    data = re.split('[:]',org)
    print(data)
    if data[0] == "public":
        print(len(re.split('[:]',org)))
        if len(re.split('[:]',org)) == 4:
            github_orgname = data[2]
            github_orgrepo = data[3]
            URL =  "https://github.com/"+github_orgname+"/"+github_orgrepo+".git"
            urls.append(URL)

        if len(re.split('[:]',org)) == 3:
            data = re.split('[:]',org)
            github_orgname = data[2]
            URL = "https://api.github.com/orgs/"+github_orgname+"/repos"
            print("Without repo => ",URL)
            response = requests.get(url = URL)
            for x in range(len(response.json())):
                urls.append(response.json()[x]["clone_url"])

    if data[0] == "private":
        pass

    return urls

def _fetch_gitlab_org_urls(orgs):
    urls = []
    if len(re.split('[:]',orgs)) == 2:
        data = re.split('[:]',orgs)
        gitlab_orgs = data[0]
        URL = "https://api.gitlab.com/orgs/"+gitlab_orgs+"/repos"
        print(URL)
        response = requests.get(url = URL)
        for x in range(len(response.json())):
            if data[1]:
                urls.append(response.json()[x]["clone_url"])
            else:
                urls.append(response.json()[x]["clone_url"])

    return urls


def _scan_users_repo(users,plateform):
    for user in users:
        if plateform == "github":
            urls = _fetch_github_repo_urls(user)
        if plateform == "gitlab":
            urls = _fetch_gitlab_repo_urls(user)
        for url in urls:
            url_info = parse(url)
            command = f"trivy repo --format template --template '@trivyreportformats/html.tpl' -o reports/{url_info.host}-{url_info.repo}.html {url}"
            os.system(command)

def _scan_org_repo(orgs,plateform):
    for org in orgs:
        if plateform == "github":
            urls = _fetch_github_org_urls(org)
        if plateform == "gitlab":
            urls = _fetch_gitlab_org_urls(org)
        for url in urls:
            url_info = parse(url)
            command = f"trivy repo --format template --template '@trivyreportformats/html.tpl' -o reports/{url_info.host}-{url_info.repo}.html {url}"
            os.system(command)


def _scanFactory(properties, args):

    try:

        for property in properties:
            LOGGER.info(f"Start to fetching the config file")
            if property == "repositories":
                LOGGER.info(f"Start fetching the plateforms")
                for plateform in properties['repositories']['specs']['plateforms']:
                    if plateform == "github":
                        LOGGER.info(f"Start to fetching the github spec")
                        if properties['repositories']['specs']['plateforms']['github']['users']:
                            github_users = properties['repositories']['specs']['plateforms']['github']['users']
                            LOGGER.info(f"Fetched gitub users data are : {github_users}")
                            _scan_users_repo(github_users,plateform)
                        if properties['repositories']['specs']['plateforms']['github']['organisations']:
                            github_orgs = properties['repositories']['specs']['plateforms']['github']['organisations']
                            LOGGER.info(f"Fetched gitub users data are : {github_orgs}")
                            _scan_org_repo(github_orgs,plateform)

                    if plateform == "gitlab":
                        LOGGER.info(f"Start to fetching the plateform gitlab spec")
                        if properties['repositories']['specs']['plateforms']['gitlab']['users']:
                            gitlab_users = properties['repositories']['specs']['plateforms']['gitlab']['users']
                            LOGGER.info(f"Fetched gitub users data are : {gitlab_users}")
                            _scan_users_repo(gitlab_users,plateform)
                        if properties['repositories']['specs']['plateforms']['gitlab']['organisations']:
                            gitlab_orgs = properties['repositories']['specs']['plateforms']['gitlab']['organisations']
                            LOGGER.info(f"Fetched gitub users data are : {gitlab_orgs}")
                            _scan_org_repo(gitlab_orgs,plateform)


    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('Urls Failure!!!! .. Please mention valid Urls in property file or use valid structure of Urls section ').with_traceback(
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
