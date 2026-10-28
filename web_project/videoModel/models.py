from django.db import models
from django.utils import timezone
from modelYolo.models import YoloModel
from user.models import SysUser

class Video(models.Model):
    STATUS_CHOICES = (
        ('pending', '等待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败')
    )
    
    video_file = models.FileField(upload_to='videos/', verbose_name='视频文件')
    original_filename = models.CharField(max_length=255, verbose_name='原始文件名')
    model = models.ForeignKey(YoloModel, on_delete=models.SET_NULL, null=True, verbose_name='使用的模型')
    detection_time = models.DateTimeField(default=timezone.now, verbose_name='检测时间')
    result_video = models.FileField(upload_to='videos/', null=True, blank=True, verbose_name='检测结果视频')
    detection_result = models.JSONField(null=True, blank=True, verbose_name='检测结果')  # 存储检测结果
    iou_threshold = models.FloatField(default=0.45, verbose_name='IoU阈值')
    confidence_threshold = models.FloatField(default=0.25, verbose_name='置信度阈值')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    creator = models.ForeignKey(SysUser, on_delete=models.SET_NULL, null=True, verbose_name="创建者")

    class Meta:
        verbose_name = '视频检测'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = "video"

    def __str__(self):
        return f'{self.original_filename} - {self.detection_time}'
