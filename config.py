import os
basedir = os.path.abspath(os.path.dirname(__file__))

POSTGRES = {
    'user': os.getenv('DB_USER'),
    'pw': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}


class BaseConfig(object):
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = os.getenv('GMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')

    # mail accounts
    MAIL_DEFAULT_SENDER = 'from@example.com'

    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

    OAUTH_CREDENTIALS = {
        'facebook': {
            'id': os.getenv('FACEBOOK_ID'),
            'secret': os.getenv('FACEBOOK_SECRET')
        },
        'twitter': {
            'id': os.getenv('TWITTER_CONSUMER_KEY'),
            'secret': os.getenv('TWITTER_CONSUMER_SECRET')
        },
        'google': {
            'id': os.getenv('GOOGLE_ID'),
            'secret': os.getenv('GOOGLE_SECRET')
        }
    }


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG_TB_ENABLED = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
