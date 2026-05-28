from flask import Blueprint

router = Blueprint("announcements", __name__, url_prefix="/announcements")


@router.route("/")
def get_health():
    return "Healthy"


@router.route("/liveness")
def get_liveness():
    return "Live"


@router.route("/readiness")
def get_readiness():
    return "Ready"
