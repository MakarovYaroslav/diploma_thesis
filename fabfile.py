import os
from fabric.api import cd, env, prefix, sudo, task, settings, run, shell_env
from fabric.contrib.files import exists

PROJECT_NAME = os.getenv('PROJECT_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
PROJECT_PATH = os.getenv('PROJECT_PATH')
PROJECT_ROOT = os.path.join(PROJECT_PATH, PROJECT_NAME)
REPO = '%s/%s.git' % (os.getenv('REPO'), PROJECT_NAME)

env.hosts = ['%s@%s:%s' % (os.getenv('HOST_USER'), os.getenv('HOST'),
                           os.getenv('HOST_PORT'))]
env.user = os.getenv('HOST_USER')
env.password = os.getenv('HOST_PASSWORD')


def install_system_packages():
    sudo('apt-get -y install python3')
    sudo('apt-get -y install nginx')
    sudo('apt-get -y install python3-pip python3-dev libpq-dev postgresql '
         'postgresql-contrib')
    sudo('apt-get -y install git')
    run('pip3 install virtualenv --user')


def create_database():
    with settings(warn_only=True):
        sudo('su - postgres psql -c "createdb %s"' % DB_NAME)


def change_postgres_user_password():
    command = "alter user postgres with password '%s'" % DB_PASSWORD
    sudo('sudo -u postgres psql -c "%s"' % command)


def clone_or_pull_git_repo():
    if not exists(PROJECT_ROOT, use_sudo=True):
        sudo('mkdir -p %s' % PROJECT_PATH)
        sudo('chown -R %s %s' % (env.user, PROJECT_PATH))
        with(cd(PROJECT_PATH)):
            run('git clone %s' % REPO)
    else:
        with cd(PROJECT_ROOT):
            run('git pull origin')


def install_pip_requirements():
    with cd(PROJECT_PATH):
        run('python3 -m virtualenv %s' % PROJECT_NAME)
    with cd(PROJECT_ROOT):
        run('source bin/activate && pip3 install -r requirements.txt')


def download_nltk_data():
    run("""python3 -c "import nltk; nltk.download('all')" """)


def set_plotly_credentials():
    run("""python3 -c "import plotly;plotly.tools.set_credentials_file(
    username='%s', api_key='%s')" """ % (os.getenv('PLOTLY_USERNAME'),
                                         os.getenv('PLOTLY_API_KEY')))


def create_db_with_admin():
    run('python3 create_db_with_admin.py')


def create_nginx_symlink_from_tpl(tpl_filename):
    nginx_path = os.path.join('/etc', 'nginx')
    run('PROJECT_PATH=%s PROJECT_NAME=%s HOST=%s envtpl %s --keep-template' % (
        PROJECT_PATH, PROJECT_NAME, os.getenv('HOST'),
        os.path.join('deploy_configs', tpl_filename)))
    sudo('chmod -R 777 %s' % nginx_path)
    run('ln -sf %s %s' % (
        os.path.join(PROJECT_PATH, PROJECT_NAME,
                     'deploy_configs', 'nginx.conf'),
        os.path.join(nginx_path, 'nginx.conf')))
    sudo('service nginx restart')


def create_uwsgi_config_from_tpl(tpl_filename):
    run('PROJECT_NAME=%s envtpl %s --keep-template' % (
        PROJECT_NAME, os.path.join('deploy_configs', tpl_filename)))
    with settings(warn_only=True):
        sudo('killall -9 uwsgi')
    run('uwsgi --ini deploy_configs/uwsgi.ini')


def initialize_env_vars():
    return shell_env(
        DB_USER=os.getenv('DB_USER'),
        DB_PASSWORD=DB_PASSWORD,
        DB_NAME=DB_NAME,
        DB_HOST=os.getenv('DB_HOST'),
        DB_PORT=os.getenv('DB_PORT'),
        ADMIN_EMAIL=os.getenv('ADMIN_EMAIL'),
        ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD'),
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SECURITY_PASSWORD_SALT=os.getenv('SECURITY_PASSWORD_SALT'),
        GMAIL_USERNAME=os.getenv('GMAIL_USERNAME'),
        GMAIL_PASSWORD=os.getenv('GMAIL_PASSWORD'),
        FACEBOOK_ID=os.getenv('FACEBOOK_ID'),
        FACEBOOK_SECRET=os.getenv('FACEBOOK_SECRET'),
        GOOGLE_ID=os.getenv('GOOGLE_ID'),
        GOOGLE_SECRET=os.getenv('GOOGLE_SECRET'),
        REDDIT_USER_AGENT=os.getenv('REDDIT_USER_AGENT'),
        REDDIT_CLIENT_ID=os.getenv('REDDIT_CLIENT_ID'),
        REDDIT_CLIENT_SECRET=os.getenv('REDDIT_CLIENT_SECRET'),
        REDDIT_CLIENT_USERNAME=os.getenv('REDDIT_CLIENT_USERNAME'),
        REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD'),
        TWITTER_CONSUMER_KEY=os.getenv('TWITTER_CONSUMER_KEY'),
        TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET'),
        TWITTER_ACCESS_KEY=os.getenv('TWITTER_ACCESS_KEY'),
        TWITTER_ACCESS_SECRET=os.getenv('TWITTER_ACCESS_SECRET'))


@task
def deploy():
    install_system_packages()
    change_postgres_user_password()
    create_database()
    clone_or_pull_git_repo()
    install_pip_requirements()
    with cd(PROJECT_ROOT), initialize_env_vars(), prefix('source bin/activate'):
        download_nltk_data()
        set_plotly_credentials()
        create_db_with_admin()
        create_nginx_symlink_from_tpl('nginx.conf.tpl')
        create_uwsgi_config_from_tpl('uwsgi.ini.tpl')


@task
def deploy_with_train():
    install_system_packages()
    change_postgres_user_password()
    create_database()
    clone_or_pull_git_repo()
    install_pip_requirements()
    with cd(PROJECT_ROOT), initialize_env_vars(), prefix('source bin/activate'):
        download_nltk_data()
        set_plotly_credentials()
        run('python3 sentiment/save_sentiment_dataset.py')
        run('python3 sentiment/train.py')
        run('python3 lda/createuci.py')
        run('python3 lda/trainmodel.py')
        create_db_with_admin()
        create_nginx_symlink_from_tpl('nginx.conf.tpl')
        create_uwsgi_config_from_tpl('uwsgi.ini.tpl')
