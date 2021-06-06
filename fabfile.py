from fabric.decorators import hosts
from fabric.api import *


@hosts(['root@109.68.212.98'])
def dep():
    with cd('/root/medAppApi/'):
        run('git pull')
        with prefix('source venv/bin/activate'):
            run('python manage.py makemigrations')
            run('python manage.py migrate')
            run('sudo killall gunicorn')



