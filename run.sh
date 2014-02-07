#!/bin/bash
# execute le serveur depuis upstart.
 
export VIRTUAL_ENV=/root/projects/moi-candidat/virtenv

cd /root/projects/moi-candidat/
source virtenv/bin/activate
$VIRTUAL_ENV/bin/python moi_candidat/manage.py runserver >> /var/log/moi-candidat.log 2>&1

