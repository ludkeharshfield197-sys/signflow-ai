from django.core.management.base import BaseCommand
from CameraModel.models import CameraDetection
import os

class Command(BaseCommand):
    help = '清理所有摄像头帧记录和相关图片文件'

    def handle(self, *args, **options):
        # 获取所有需要删除的图像文件路径
        image_paths = []
        for detection in CameraDetection.objects.all():
            if detection.image:
                image_paths.append(detection.image.path)
        
        # 删除所有CameraDetection记录
        deleted_count = CameraDetection.objects.count()
        CameraDetection.objects.all().delete()
        
        # 删除对应的图像文件
        deleted_files = 0
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    deleted_files += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"删除文件失败: {path}, 错误: {e}"))
        
        self.stdout.write(
            self.style.SUCCESS(f'成功删除 {deleted_count} 条记录和 {deleted_files} 个文件')
        ) 