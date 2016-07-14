FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y \
		gcc \
		gettext \
		apt-utils \
		mysql-client libmysqlclient-dev \
		postgresql-client libpq-dev \
		sqlite3 \
		postgresql \


	--no-install-recommends && rm -rf /var/lib/apt/lists/*

