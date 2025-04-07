import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+mysqlconnector://tomasdeane1:tomaspassword@tomasdeane1.mysql.pythonanywhere-services.com/tomasdeane1$default'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY', '1ecbdaa3-aa0d-4f28-ad9a-5cddfa2c42eb')
