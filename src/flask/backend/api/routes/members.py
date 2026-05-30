from flask import Blueprint

router = Blueprint("members", __name__)


@router.route("/members")
def get_health():
    _tag = "members"
    return "Healthy"


@router.route("/members/liveness")
def get_liveness():
    _tag = "members"
    return "Live"


@router.route("/members/readiness")
def get_readiness():
    _tag = "members"
    return "Ready"
