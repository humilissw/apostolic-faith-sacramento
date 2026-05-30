from flask import Blueprint

router = Blueprint("announcements", __name__)


@router.route("/announcements")
def get_health():
    _tag = "announcements"
    return "Healthy"


@router.route("/announcements/liveness")
def get_liveness():
    _tag = "announcements"
    return "Live"


@router.route("/announcements/readiness")
def get_readiness():
    _tag = "announcements"
    return "Ready"
