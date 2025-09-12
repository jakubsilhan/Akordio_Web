from flask import current_app
from app.services.fullsong_service import Fullsong_Service
from app.services.online_service import Online_Service
from app.services.separation_service import Separation_Service

def get_fullsong_service() -> Fullsong_Service:
    return current_app.extensions["fullsong_service"]

def get_online_service() -> Online_Service:
    return current_app.extensions["online_service"]

def get_separation_service() -> Separation_Service:
    return current_app.extensions["separation_service"]