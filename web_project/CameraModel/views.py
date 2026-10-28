"""Retired v0 camera HTTP endpoints.

Authenticated camera sessions now use ``/api/v1/camera/tickets/`` and the
bounded ``/ws/camera/<session_id>/`` channel.
"""

from api.legacy import RetiredMediaEndpointView, retired_media_endpoint


class CameraView(RetiredMediaEndpointView):
    pass


export_results = retired_media_endpoint
camera_sessions = retired_media_endpoint
session_detail = retired_media_endpoint
clean_frame_records = retired_media_endpoint
dome = retired_media_endpoint
generate_sentence_from_detection = retired_media_endpoint
