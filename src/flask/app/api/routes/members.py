from flask import Blueprint

router = Blueprint("members", __name__, url_prefix="/members")


@router.route("/")
def get_health():
    return "Healthy"


@router.route("/liveness")
def get_liveness():
    return "Live"


@router.route("/readiness")
def get_readiness():
    return "Ready"
