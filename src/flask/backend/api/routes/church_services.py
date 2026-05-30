from flask import Blueprint

router = Blueprint("church_services", __name__)


@router.route("/church-services")
def get_health():
    _tag = "church-services"
    return "Healthy"


@router.route("/church-services/liveness")
def get_liveness():
    _tag = "church-services"
    return "Live"


@router.route("/church-services/readiness")
def get_readiness():
    _tag = "church-services"
    return "Ready"
