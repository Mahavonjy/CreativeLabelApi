FROM python:3.7.2-slim

MAINTAINER Cynthion Mahavonjy <mahavonjy.cynthion@gmail.com>

COPY . /usr/src/app/
WORKDIR /usr/src/app/

COPY supervisor_creative.conf /etc/supervisor/conf.d/supervisord.conf

# install dependencies
RUN apt-get update && \
	apt-get install -y ffmpeg openssh-server supervisor && mkdir -p /var/log/creative_api && \
	touch /var/log/creative_api/creative_api.err.log && touch /var/log/creative_api/creative_api.out.log && \
	apt-get install curl -y && apt-get install libsndfile1 -y && apt-get install -y --no-install-recommends gcc

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 80
CMD ["/bin/bash", "entrypoint.sh"]