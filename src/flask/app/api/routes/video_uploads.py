from flask import Blueprint, jsonify

from app.api.deps import get_current_user, get_db
from app.repositories.video_upload_repo import VideoUploadRepository
from app.requests.video_upload_request import VideoUploadCreate, VideoUploadUpdate
from app.responses.video_upload_response import (
    VideoUploadPublic,
    VideoUploadPublicWithUrl,
    VideoUploadsPublic,
)

router = Blueprint("video_uploads", __name__, url_prefix="/video-uploads")


@router.route("/liveness")
def health_check():
    return "Live"


@router.route("/readiness")
def readiness_check():
    return "Ready"


@router.route("/", methods=["GET"])
def read_video_uploads(skip: int = 0, limit: int = 100):
    session = get_db()
    repository = VideoUploadRepository(session=session)
    video_uploads, total_count = repository.get_all(skip=skip, limit=limit)
    video_upload_data = [
        VideoUploadPublicWithUrl(
            id=v.id,
            upload_location=v.upload_location,
            upload_name=v.upload_name,
            description=v.description,
            reference_text=v.reference_text,
            speaker_name=v.speaker_name,
            media_association_date=v.media_association_date,
            created_on=v.created_on,
            updated_on=v.updated_on,
            download_url=v.upload_location,
        )
        for v in video_uploads
    ]
    return jsonify(VideoUploadsPublic(data=video_upload_data, count=total_count).model_dump())


@router.route("/<video_upload_id>", methods=["GET"])
def read_video_upload_by_id(video_upload_id: str):
    session = get_db()
    repository = VideoUploadRepository(session=session)
    video_upload = repository.get_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        return jsonify({"detail": "Video upload not found"}), 404
    return jsonify(VideoUploadPublic.model_validate(video_upload).model_dump())


@router.route("/", methods=["POST"])
def create_video_upload_endpoint():
    from flask import request

    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    video_upload_in = VideoUploadCreate(**data)
    repository = VideoUploadRepository(session=session)
    video_upload = repository.create(video_upload_in=video_upload_in, owner_id=current_user.id)
    return jsonify(VideoUploadPublic.model_validate(video_upload).model_dump()), 201


@router.route("/<video_upload_id>", methods=["PATCH"])
def update_video_upload_endpoint(video_upload_id: str):
    from flask import request

    session = get_db()
    current_user = get_current_user()
    data = request.get_json()
    video_upload_in = VideoUploadUpdate(**data)
    repository = VideoUploadRepository(session=session)
    video_upload = repository.get_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        return jsonify({"detail": "Video upload not found"}), 404
    if current_user.id != video_upload.owner_id and not current_user.is_superuser:
        return jsonify({"detail": "Not authorized to update this video upload"}), 403
    video_upload = repository.update(db_video_upload=video_upload, video_upload_in=video_upload_in)
    return jsonify(VideoUploadPublic.model_validate(video_upload).model_dump())


@router.route("/<video_upload_id>", methods=["DELETE"])
def delete_video_upload_endpoint(video_upload_id: str):
    session = get_db()
    current_user = get_current_user()
    repository = VideoUploadRepository(session=session)
    video_upload = repository.get_by_id(video_upload_id=video_upload_id)
    if not video_upload:
        return jsonify({"detail": "Video upload not found"}), 404
    if current_user.id != video_upload.owner_id and not current_user.is_superuser:
        return jsonify({"detail": "Not authorized to delete this video upload"}), 403
    repository.delete(db_video_upload=video_upload)
    return jsonify({"message": "Video upload deleted successfully"})
