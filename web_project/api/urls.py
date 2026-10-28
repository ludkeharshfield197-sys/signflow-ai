from django.urls import path

from api.admin_views import (
    AdminRoleListAPIView,
    AdminSystemAPIView,
    AdminUserListAPIView,
)
from api.product_views import (
    AnalyticsAPIView,
    ModelCatalogAPIView,
    OverviewAPIView,
    PublicModelMetricsAPIView,
    ResultConfirmAPIView,
    ResultDetailAPIView,
    ResultListAPIView,
    ResultMediaAPIView,
    ResultRerunAPIView,
    ResultVersionsAPIView,
)
from api.views import (
    CameraTicketAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    RefreshAPIView,
    RegisterAPIView,
)
from detections.views import (
    DetectionJobCancelAPIView,
    DetectionJobDetailAPIView,
    DetectionJobListCreateAPIView,
    DetectionJobRetryAPIView,
    DetectionJobSaveAPIView,
)

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/refresh/", RefreshAPIView.as_view(), name="auth-refresh"),
    path("auth/me/", MeAPIView.as_view(), name="auth-me"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("camera/tickets/", CameraTicketAPIView.as_view(), name="camera-ticket"),
    path("admin/users/", AdminUserListAPIView.as_view(), name="admin-user-list"),
    path("admin/roles/", AdminRoleListAPIView.as_view(), name="admin-role-list"),
    path("admin/system/", AdminSystemAPIView.as_view(), name="admin-system"),
    path("analytics/", AnalyticsAPIView.as_view(), name="analytics"),
    path("overview/", OverviewAPIView.as_view(), name="overview"),
    path("results/", ResultListAPIView.as_view(), name="result-list"),
    path("results/<str:result_id>/", ResultDetailAPIView.as_view(), name="result-detail"),
    path(
        "results/<str:result_id>/media/",
        ResultMediaAPIView.as_view(),
        name="result-media",
    ),
    path(
        "results/<str:result_id>/confirm/",
        ResultConfirmAPIView.as_view(),
        name="result-confirm",
    ),
    path(
        "results/<str:result_id>/rerun/",
        ResultRerunAPIView.as_view(),
        name="result-rerun",
    ),
    path(
        "results/<str:result_id>/versions/",
        ResultVersionsAPIView.as_view(),
        name="result-versions",
    ),
    path("models/", ModelCatalogAPIView.as_view(), name="model-catalog"),
    path(
        "public/model-metrics/",
        PublicModelMetricsAPIView.as_view(),
        name="public-model-metrics",
    ),
    path("detections/", DetectionJobListCreateAPIView.as_view(), name="detection-create"),
    path("detections/jobs/", DetectionJobListCreateAPIView.as_view(), name="detection-job-create"),
    path(
        "detections/jobs/<str:job_id>/",
        DetectionJobDetailAPIView.as_view(),
        name="detection-job-detail",
    ),
    path(
        "detections/jobs/<str:job_id>/cancel/",
        DetectionJobCancelAPIView.as_view(),
        name="detection-job-cancel",
    ),
    path(
        "detections/jobs/<str:job_id>/save/",
        DetectionJobSaveAPIView.as_view(),
        name="detection-job-save",
    ),
    path(
        "detections/jobs/<str:job_id>/retry/",
        DetectionJobRetryAPIView.as_view(),
        name="detection-job-retry",
    ),
]
