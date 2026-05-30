"""Routes for feature flag management."""

from flask import Blueprint, jsonify, request

from backend.api.deps import get_current_active_superuser, get_db
from backend.models import FeatureFlagPublic, FeatureFlagsPublic
from backend.repositories.feature_flag_repo import FeatureFlagRepository
from backend.services.feature_flag_service import FeatureFlagService, KNOWN_FEATURE_FLAGS

router = Blueprint("feature_flags", __name__)


@router.route("/feature-flags/names")
def get_enabled_flag_names():
    _tag = "feature-flags"
    session = get_db()
    service = FeatureFlagService(FeatureFlagRepository(session))
    return jsonify(service.get_enabled_names())


@router.route("/feature-flags/known")
def get_known_feature_flags():
    _tag = "feature-flags"
    return jsonify(
        {
            name: {
                "display_name": meta["display_name"],
                "description": meta["description"],
                "icon": meta["icon"],
                "required_scopes": meta.get("required_scopes", []),
            }
            for name, meta in KNOWN_FEATURE_FLAGS.items()
        }
    )


@router.route("/feature-flags/pre-seed", methods=["POST"])
def pre_seed_feature_flags():
    _tag = "feature-flags"
    session = get_db()
    _ = get_current_active_superuser()
    service = FeatureFlagService(FeatureFlagRepository(session))
    service.pre_seed_flags()
    items, total = service.get_all()
    return jsonify(FeatureFlagsPublic(data=[FeatureFlagPublic.model_validate(i.model_dump()) for i in items], count=total).model_dump())


@router.route("/feature-flags")
def list_feature_flags():
    _tag = "feature-flags"
    session = get_db()
    service = FeatureFlagService(FeatureFlagRepository(session))
    items, total = service.get_all()
    return jsonify(FeatureFlagsPublic(data=[FeatureFlagPublic.model_validate(i.model_dump()) for i in items], count=total).model_dump())


@router.route("/feature-flags/<flag_name>", methods=["PATCH"])
def update_feature_flag(flag_name: str):
    _tag = "feature-flags"
    session = get_db()
    _ = get_current_active_superuser()
    data = request.get_json()
    service = FeatureFlagService(FeatureFlagRepository(session))
    flag = service.get_by_name(flag_name)
    if not flag:
        return jsonify({"detail": f"Feature flag '{flag_name}' not found"}), 404
    update_data = data or {}
    updated = service.update_enabled(flag, update_data.get("is_enabled", flag.is_enabled))
    return jsonify(FeatureFlagPublic.model_validate(updated.model_dump()).model_dump())
