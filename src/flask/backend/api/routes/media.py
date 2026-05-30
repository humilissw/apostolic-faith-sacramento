from flask import Blueprint, jsonify

from backend.api.deps import get_current_user, get_db, require_scope
from backend.crud import create_media
from backend.repositories.media_repo import MediaRepository
from backend.requests.media_request import MediaCreate, MediaUpdate
from backend.responses.media_response import MediaPublic

router = Blueprint("media", __name__)
media_service = None


@router.route("/media/liveness")
def get_liveness():
    _tag = "media"
    return "Live"


@router.route("/media/readiness")
def get_readiness():
    _tag = "media"
    return "Ready"


@router.route("/media", methods=["GET"])
@require_scope("api:all")
def read_media(skip: int = 0, limit: int = 100):
    _tag = "media"
    session = get_db()
    repository = MediaRepository(session=session)
    medias, total_count = repository.get_all(skip=skip, limit=limit)
    media_data = [
        {
            "id": m.id,
            "name": m.name,
            "uploaded_on": m.uploaded_on,
            "created_on": m.created_on,
            "updated_on": m.updated_on,
            "download_url": f"/media/{m.id}/download",
        }
        for m in medias
    ]
    return jsonify({"data": media_data, "count": total_count})


@router.route("/media/<string:media_id>", methods=["GET"])
@require_scope("api:all")
def read_media_by_id(media_id: str):
    _tag = "media"
    session = get_db()
    repository = MediaRepository(session=session)
    media = repository.get_by_id(media_id=media_id)
    if not media:
        return jsonify({"detail": "Media not found"}), 404
    return jsonify(MediaPublic.model_validate(media.model_dump()).model_dump())


@router.route("/media", methods=["POST"])
@require_scope("api:all")
def create_media_endpoint():
    _tag = "media"
    from flask import request

    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    media_in = MediaCreate(**data)
    media = create_media(session=session, media_in=media_in, owner_id=current_user.id)
    return jsonify(MediaPublic.model_validate(media.model_dump()).model_dump()), 201


@router.route("/media/<string:media_id>", methods=["PATCH"])
@require_scope("api:all")
def update_media_endpoint(media_id: str):
    _tag = "media"
    from flask import request

    session = get_db()
    current_user = get_current_user()
    repository = MediaRepository(session=session)
    media = repository.get_by_id(media_id=media_id)
    if not media:
        return jsonify({"detail": "Media not found"}), 404
    if current_user.id != media.owner_id and not current_user.is_superuser:
        return jsonify({"detail": "Not authorized to update this media"}), 403
    data = request.get_json()
    media_in = MediaUpdate(**data)
    media = repository.update(db_media=media, media_in=media_in)
    return jsonify(MediaPublic.model_validate(media.model_dump()).model_dump())


@router.route("/media/<string:media_id>", methods=["DELETE"])
@require_scope("api:all")
def delete_media_endpoint(media_id: str):
    _tag = "media"
    session = get_db()
    current_user = get_current_user()
    repository = MediaRepository(session=session)
    media = repository.get_by_id(media_id=media_id)
    if not media:
        return jsonify({"detail": "Media not found"}), 404
    if current_user.id != media.owner_id and not current_user.is_superuser:
        return jsonify({"detail": "Not authorized to delete this media"}), 403
    repository.delete(db_media=media)
    return jsonify({"message": "Media deleted successfully"})
