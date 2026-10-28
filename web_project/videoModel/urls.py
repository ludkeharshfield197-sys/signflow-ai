from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_detection, name='submit_detection'),  # 提交视频检测任务
    path('stream/<int:task_id>/', views.get_detection_stream, name='get_detection_stream'),  # 获取检测结果流
    path('result/<int:task_id>/', views.get_detection_result, name='get_detection_result'),  # 获取检测结果数据
    path('export/', views.export, name='video_export'),  # 主要导出路径
    path('export/text/', views.export, name='export_text'),  # 重定向到主导出函数
    path('export/video/', views.export, name='export_videos'),  # 重定向到主导出函数
    path('list/', views.video_list, name='video_list'),  # 获取视频列表
    path('delete/', views.video_delete, name='video_delete'),  # 删除视频
    path('detail/<int:video_id>/', views.video_detail, name='video_detail'),  # 获取视频详情
    path('sentence/', views.generate_sentence_from_detection, name='generate_sentence'),
]