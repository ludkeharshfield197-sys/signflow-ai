from django.db import models
from django.utils import timezone
from user.models import SysUser

class Image(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='原始图片')
    result_image = models.ImageField(upload_to='results/', verbose_name='检测结果图片', null=True, blank=True)
    upload_time = models.DateTimeField(default=timezone.now, verbose_name='上传时间')
    model_name = models.CharField(max_length=100, verbose_name='使用的模型名称')
    iou_threshold = models.FloatField(default=0.45, verbose_name='IoU阈值')
    conf_threshold = models.FloatField(default=0.25, verbose_name='置信度阈值')
    result = models.JSONField(verbose_name='识别结果', null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', verbose_name='识别状态')
    error_message = models.TextField(verbose_name='错误信息', null=True, blank=True)
    creator = models.ForeignKey(SysUser, on_delete=models.SET_NULL, null=True, verbose_name="创建者")

    class Meta:
        db_table = 'image'
        verbose_name = '图片识别'
        verbose_name_plural = verbose_name
        ordering = ['-upload_time']

    def __str__(self):
        return f'Image {self.id} - {self.upload_time}'
