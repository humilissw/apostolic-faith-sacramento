from flask import Blueprint, jsonify

from app.utils import generate_test_email, send_email

router = Blueprint("utils", __name__, url_prefix="/utils")


@router.route("/test-email/", methods=["POST"])
def test_email(email_to: str = None):
    import flask

    email_to = flask.request.args.get("email_to")
    if not email_to:
        from flask import request

        data = request.get_json(silent=True) or {}
        email_to = data.get("email_to")
    from pydantic.networks import EmailStr

    email_to = EmailStr(email_to)  # type: ignore

    email_data = generate_test_email(email_to=email_to)
    send_email(email_to=email_to, subject=email_data.subject, html_content=email_data.html_content)
    return jsonify({"message": "Test email sent"})


@router.route("/health-check/")
def health_check():
    return "Healthy"
