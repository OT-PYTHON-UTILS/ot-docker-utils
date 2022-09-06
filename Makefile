VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/image_scanner_sample_config.yml

scan_build:
	docker build -t opstree/image_scanner:$(VERSION) -f Scan_Images_Dockerfile .
scan_run:
	docker run -it --rm --name image_scanner -v ${CONF_PATH}:/etc/image_scanner_config.yml:ro -e CONF_PATH='/etc/image_scanner_config.yml' -v ~/.aws:/root/.aws -v  /var/run/docker.sock:/var/run/docker.sock opstree/image_scanner:${VERSION} 
