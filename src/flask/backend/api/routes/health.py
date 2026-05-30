from flask import Blueprint

router = Blueprint("health", __name__)


@router.route("/health")
def get_health():
    _tag = "health"
    return "Healthy"


@router.route("/health/liveness")
def get_liveness():
    _tag = "health"
    return "Live"


@router.route("/health/readiness")
def get_readiness():
    _tag = "health"
    return "Ready"
