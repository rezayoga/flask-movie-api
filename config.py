from pathlib import Path

BASE_DIR = Path(__file__).parent
print(BASE_DIR)


class Config:
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    #    str(BASE_DIR.joinpath('db.sqlite'))
    
    SQLALCHEMY_DATABASE_URI = 'mysql://root:rezareza1985@localhost/db_movie'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = 'R3z4y0gasw@R4'
    DEVELOPER = 'Reza Yogaswara'
