from django.db import models

# Create your models here.

class Document(models.Model):
    """存储手语知识文档的模型"""
    title = models.CharField(max_length=255, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "手语知识文档"
        verbose_name_plural = "手语知识文档"

    def __str__(self):
        return self.title
