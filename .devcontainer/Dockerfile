# syntax=docker/dockerfile:1
FROM python:slim-bookworm
ARG GECKODRIVER_VERSION="0.33.0"
RUN apt-get update -y && apt-get install -y \
    git sudo man man-db readline-common bash-completion python3-argcomplete pipx tar gzip procps wget firefox-esr python3-pytest python3-pytest-cov python3-pdm \
    && wget -qO- https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux-$(arch).tar.gz \
    | tar -C /usr/local/bin -xzvf - \
    && addgroup --gid 1000 scrapy \
    && adduser --gid 1000 --uid 1000 --disabled-password --gecos "" scrapy \
    && echo "scrapy ALL=(root) NOPASSWD:ALL" >/etc/sudoers.d/scrapy
