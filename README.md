playdoh
=======

```
>>> django.VERSION
(1, 3, 1, 'final', 0)

aptitude install python-dev mysql-server python-pip python-virtualenv python-mysqldb git-core libmysqlclient-dev

CREATE USER 'cyder'@'localhost' IDENTIFIED BY '****';
GRANT ALL PRIVILEGES ON *.* TO 'cyder'@'localhost';
create database cyder;
flush priviliges;

pip install -e git+https://github.com/toastdriven/django-haystack.git@master#egg=django-haystack

pip install ipaddr

pip install Whoosh

pip install simplejson

pip install funfactory

git clone https://github.com/uberj/cyder.git /data/cyder

cd /data/cyder

git clone --recursive git://github.com/mozilla/playdoh-lib.git ./vendor

pip install -r requirements/compiled.txt

```

Sphinx Docs
===========
```
aptitude install python-sphinx
cd /data/cyder/docs
make html
```

Apache setup
==========
```
aptitude install apache2 libapache2-mod-wsgi
a2enmod rewrite
a2enmod proxy
```
