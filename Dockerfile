FROM python:3.7.4-slim-buster

WORKDIR /sirius

RUN apt-get update -y && \
  mkdir -p /usr/share/man/man1 && \
  mkdir -p /usr/share/man/man7 && \
  apt-get install -y --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip \
  libfreetype6-dev \
  libgstreamer1.0-dev \
  libjpeg-dev \
  libpq-dev \
  zlib1g-dev \
  bzip2 \
  fontconfig \
  gcc \
  phantomjs \
  wget \
  postgresql-11 \
  git

RUN apt-get autoremove -y

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar jxf phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
  rm phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
  mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs

RUN pip install --upgrade pip

ADD ./requirements.txt /sirius/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install honcho

EXPOSE 5000

ADD . .
