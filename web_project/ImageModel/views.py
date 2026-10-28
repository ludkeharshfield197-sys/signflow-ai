"""Retired v0 image endpoints.

The commercial API uses owner-scoped asynchronous detection jobs under
``/api/v1/detections/``. These names remain only so an explicitly enabled
legacy URL configuration fails with a useful migration response.
"""

from api.legacy import RetiredMediaEndpointView


class ImageDetectView(RetiredMediaEndpointView):
    pass


class ImageExportView(RetiredMediaEndpointView):
    pass


class ImageUploadView(RetiredMediaEndpointView):
    pass


class ImageListView(RetiredMediaEndpointView):
    pass


class ImageDeleteView(RetiredMediaEndpointView):
    pass


class TextExportView(RetiredMediaEndpointView):
    pass


class ImageFileExportView(RetiredMediaEndpointView):
    pass
