from django.db import models
from django.utils import timezone
from modelYolo.models import YoloModel
from user.models import SysUser

# Create your models here.

class CameraSession(models.Model):
    """摄像头识别会话记录"""
    session_id = models.CharField(max_length=36, unique=True, verbose_name='会话ID')
    model = models.ForeignKey(YoloModel, on_delete=models.SET_NULL, null=True, verbose_name='使用的模型')
    iou_threshold = models.FloatField(default=0.45, verbose_name='IoU阈值')
    confidence_threshold = models.FloatField(default=0.25, verbose_name='置信度阈值')
    start_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    detection_count = models.IntegerField(default=0, verbose_name='检测次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    creator = models.ForeignKey(SysUser, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    # 新增检测结果存储字段
    detection_results = models.JSONField(null=True, blank=True, verbose_name='检测结果')
    result_video = models.FileField(upload_to='camera_results/', null=True, blank=True, verbose_name='结果视频')
    
    class Meta:
        verbose_name = '摄像头会话'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'会话 {self.session_id} - {self.model.name if self.model else "未知模型"}'

class CameraDetection(models.Model):
    """单次摄像头检测结果"""
    session = models.ForeignKey(CameraSession, on_delete=models.CASCADE, related_name='detections', verbose_name='会话')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='检测时间')
    frame_number = models.IntegerField(default=0, verbose_name='帧序号')
    detection_result = models.JSONField(verbose_name='检测结果')
    image = models.ImageField(upload_to='camera/frames/', null=True, blank=True, verbose_name='检测帧图像')
    
    class Meta:
        verbose_name = '摄像头检测结果'
        verbose_name_plural = verbose_name
        ordering = ['session', 'frame_number']
