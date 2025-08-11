import os

# Flask automatically loads the root .env file

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")