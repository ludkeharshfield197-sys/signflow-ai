from django.core.management.base import BaseCommand
from CameraModel.models import CameraDetection
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = '立即清理所有摄像头帧记录和相关图片文件'

    def handle(self, *args, **options):
        try:
            # 获取所有帧记录
            detections = CameraDetection.objects.all()
            count = detections.count()
            
            self.stdout.write(self.style.WARNING(f'即将删除 {count} 条帧记录'))
            
            # 删除所有图像文件
            image_paths = []
            for detection in detections:
                if detection.image and hasattr(detection.image, 'path') and detection.image.path:
                    image_paths.append(detection.image.path)
            
            # 删除记录
            detections.delete()
            
            # 删除图像文件
            deleted_files = 0
            for path in image_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        deleted_files += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"删除文件失败: {path}, 错误: {e}"))
            
            # 强制清理media/camera_frames目录
            camera_frames_dir = os.path.join(settings.MEDIA_ROOT, 'camera_frames')
            if os.path.exists(camera_frames_dir):
                try:
                    # 直接删除整个目录并重建
                    shutil.rmtree(camera_frames_dir)
                    os.makedirs(camera_frames_dir, exist_ok=True)
                    self.stdout.write(self.style.SUCCESS(f'已重建camera_frames目录'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"清理camera_frames目录失败: {e}"))
            
            # 检查是否清理干净
            remaining = CameraDetection.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(f'成功删除 {count} 条记录和 {deleted_files} 个文件')
            )
            
            if remaining > 0:
                self.stdout.write(
                    self.style.ERROR(f'警告: 仍有 {remaining} 条记录未删除!')
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'清理过程发生错误: {e}')) 