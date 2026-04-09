from flask import current_app
from app.services.fullsong_service import Fullsong_Service
from app.services.online_service import Online_Service
from app.services.separation_service import Separation_Service

_fullsong_service = None
_separation_service = None
_online_service = None


def get_fullsong_service():
    global _fullsong_service
    if _fullsong_service is None:
        _fullsong_service = Fullsong_Service()
    return _fullsong_service


def get_separation_service():
    global _separation_service
    if _separation_service is None:
        _separation_service = Separation_Service()
    return _separation_service

def get_online_service():
    global _online_service
    if _online_service is None:
        _online_service = Online_Service()
    return _online_service