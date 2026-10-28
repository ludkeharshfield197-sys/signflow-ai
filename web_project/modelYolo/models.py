from django.db import models
from rest_framework import serializers
from user.models import SysUser


class YoloModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="模型名称")
    version = models.CharField(max_length=50, verbose_name="版本")
    size = models.CharField(max_length=20, verbose_name="文件大小")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    status = models.CharField(max_length=20, default="正常", verbose_name="状态")
    remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="备注")
    file_path = models.CharField(max_length=255, verbose_name="文件路径")
    creator = models.ForeignKey(SysUser, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    evaluation = models.JSONField(default=dict, blank=True, verbose_name="评测卡")

    class Meta:
        db_table = "yolo_model"


class YoloModelSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = YoloModel
        fields = '__all__'
    
    def get_creator_name(self, obj):
        return obj.creator.username if obj.creator else "未知"
