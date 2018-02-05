FROM debian:9.3-slim

WORKDIR /sirius

RUN apt-get update -y && mkdir -p /usr/share/man/man1 && mkdir -p /usr/share/man/man7 && apt-get install -y python python-pip libpq-dev phantomjs libfreetype6-dev fontconfig libgstreamer1.0-dev python-dev wget libjpeg-dev zlib1g-dev postgresql-9.6

RUN apt-get autoremove -y

RUN pip install --upgrade pip

ADD ./requirements.txt /sirius/requirements.txt
RUN pip install -r requirements.txt

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar jxf phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN rm phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs

RUN pip install honcho

EXPOSE 5000

ADD . .

RUN ./manage.py db upgrade

ENTRYPOINT honcho start
