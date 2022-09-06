scan_images_build:
	docker build -t opstree/image_scanner:$(VERSION) -f Scan_Images_Dockerfile .
scan_images_run:
	docker run -it --rm --name image_scanner -v ${CONF_PATH}:/etc/image_scanner_config.yml:ro -e CONF_PATH='/etc/image_scanner_config.yml' -v ~/.aws:/root/.aws -v  /var/run/docker.sock:/var/run/docker.sock opstree/image_scanner:${VERSION} 

scan_creds_build:
	docker build -t opstree/cred_scanner:$(VERSION) -f Dockerfile .
scan_creds_run:
	docker run -it --rm --name cred_scanner -v ${CONF_PATH}:/etc/scan_creds_sample_config.yml:ro -e CONF_PATH='/etc/scan_creds_sample_config.yml' -v  /var/run/docker.sock:/var/run/docker.sock opstree/cred_scanner:${VERSION} 

