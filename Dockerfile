FROM python:slim-buster AS builder

WORKDIR /opt/

COPY . .

RUN apt-get update && \
    apt-get install -y binutils libc-bin git wget apt-transport-https gnupg lsb-release

RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && \
    echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install trivy && mkdir -p reports /var/log/ot

RUN pip3 install --no-cache --upgrade -r requirements.txt

RUN pyinstaller --paths=lib scripts/scan_images.py --onefile

RUN cp dist/scan_images .

ENTRYPOINT ["./scan_images"]
