from django.urls import path
from . import views

urlpatterns = [
    path('detect/', views.ImageDetectView.as_view(), name='image_detect'),  # 图片检测
    path('export/', views.ImageExportView.as_view(), name='image_export'),  # 导出检测结果
    path('list/', views.ImageListView.as_view(), name='image_list'),  # 获取图片列表
    path('delete/', views.ImageDeleteView.as_view(), name='image_delete'),  # 删除图片
    path('export/text/', views.TextExportView.as_view(), name='export_text'), # 导出检测结果文本
    path('export/image/', views.ImageFileExportView.as_view(), name='export_images'), # 导出检测图片
]

