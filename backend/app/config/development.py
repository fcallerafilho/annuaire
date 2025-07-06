SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root_password@users_db:3306/users_db'
SQLALCHEMY_BINDS = {
    'users_db': 'mysql+pymysql://root:root_password@users_db:3306/users_db',
    'auth_db': 'mysql+pymysql://root:root_password@auth_db:3306/auth_db'
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 280,
    'pool_timeout': 20,
    'pool_pre_ping': True
}