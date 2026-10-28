"""Retired v0 video endpoints.

Video inference now runs through persisted Celery jobs rather than request
threads or streaming responses that load model weights in Django.
"""

from api.legacy import retired_media_endpoint


submit_detection = retired_media_endpoint
get_detection_stream = retired_media_endpoint
get_detection_result = retired_media_endpoint
export = retired_media_endpoint
video_list = retired_media_endpoint
video_delete = retired_media_endpoint
video_detail = retired_media_endpoint
generate_sentence_from_detection = retired_media_endpoint
