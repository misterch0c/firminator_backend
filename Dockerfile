FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN apt-get update && apt-get install -y \
		gcc \
		gettext \
		apt-utils \
		mysql-client libmysqlclient-dev \
		postgresql-client libpq-dev \
		sqlite3 \
		postgresql \
		busybox-static fakeroot git kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan \
		git build-essential libqt4-opengl mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full cabextract cramfsprogs cramfsswap squashfs-tools zlib1g-dev liblzma-dev liblzo2-dev sleuthkit openjdk-7-jdk python-crypto python-lzo python-lzma python-pip python-opengl python-qt4 python-qt4-gl python-numpy python-scipy python3-crypto python3-pip python3-opengl python3-pyqt4 python3-pyqt4.qtopengl python3-numpy python3-scipy \

	--no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/devttys0/binwalk.git
WORKDIR /usr/src/app/binwalk
RUN yes | ./deps.sh
RUN python setup.py install

EXPOSE 8000
