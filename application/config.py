from datetime import timedelta

class Config(object):
    DEBUG = False
    TESTING = False
    CACHE_TYPE = "RedisCache"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lib.db' 
    SECRET_KEY = "SECRET"
    SECURITY_PASSWORD_SALT = "SALT"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY=SECRET_KEY
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=10)
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 3
    CACHE_DEFAULT_TIMEOUT = 300
    
#====================END OF FILE====================#