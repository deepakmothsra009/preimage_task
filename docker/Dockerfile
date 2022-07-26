FROM ubuntu:20.04
RUN apt-get -qq update
RUN apt-get update
RUN apt-get install -y supervisor redis vim cron
WORKDIR /preimage_task
RUN apt-get --no-install-recommends -y install python3-dev python3-pip gnupg build-essential python3-setuptools libpq-dev gcc wget libffi-dev g++ && apt-get autoclean && rm -rf /var/lib/apt/lists/*
RUN apt-get update
ADD . /preimage_task
RUN pip3 install -r requirements.txt
ENV PROJECT_ENV docker
COPY docker/configurations.py docker_configurations.py
ADD docker docker
ENTRYPOINT ["bash","/preimage_task/docker/start.sh"]
