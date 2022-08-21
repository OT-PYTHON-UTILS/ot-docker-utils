VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/image_scanner_sample_config.yml

build:
	docker build -t opstree/image_scanner:$(VERSION) .
run:
	docker run -it --rm --name image_scanner -v ${CONF_PATH}:/etc/ot/image_scanner.yml:ro -e CONF_PATH='/etc/ot/image_scanner.yml' -v ~/.aws:/root/.aws  opstree/image_scanner:${VERSION} 