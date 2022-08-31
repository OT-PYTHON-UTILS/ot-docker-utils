VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/scan_creds_sample_config.yml

scan_build:
	docker build -t opstree/cred_scanner:$(VERSION) -f Dockerfile .
scan_run:
	docker run -it --rm --name cred_scanner -v ${CONF_PATH}:/etc/scan_creds_sample_config.yml:ro -e CONF_PATH='/etc/scan_creds_sample_config.yml' -v ~/.aws:/root/.aws -v  /var/run/docker.sock:/var/run/docker.sock opstree/cred_scanner:${VERSION} 
