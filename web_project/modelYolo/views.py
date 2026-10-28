import os
import json
from django.http import JsonResponse, FileResponse
from django.views import View
from django.core.paginator import Paginator
from .models import YoloModel, YoloModelSerializer
from django.conf import settings


class ModelListView(View):
    def post(self, request):
        """
        获取模型列表，支持按名称和版本进行模糊查询
        """
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            page_num = data.get('pageNum', 1)
            page_size = data.get('pageSize', 10)

            queryset = YoloModel.objects.all()
            if query:
                # 同时支持名称和版本的模糊查询
                queryset = queryset.filter(name__icontains=query) | queryset.filter(version__icontains=query)

            paginator = Paginator(queryset, page_size)
            page_models = paginator.page(page_num)

            model_list = YoloModelSerializer(page_models, many=True).data
            return JsonResponse({
                'code': 200,
                'data': {
                    'modelList': model_list,
                    'total': paginator.count
                }
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})


class ModelUploadView(View):
    def post(self, request):
        """
        上传模型文件
        """
        try:
            model_file = request.FILES.get('file')
            if not model_file:
                return JsonResponse({'code': 400, 'message': '未上传文件'})

            # 检查文件类型
            if not model_file.name.endswith(('.pt', '.onnx')):
                return JsonResponse({'code': 400, 'message': '仅支持.pt或.onnx格式的文件'})

            # 保存文件
            relative_path = os.path.join('model', model_file.name)
            file_path = os.path.join(settings.MODELS_ROOT, model_file.name)
            with open(file_path, 'wb+') as f:
                for chunk in model_file.chunks():
                    f.write(chunk)

            # 获取当前用户ID
            token = request.META.get('HTTP_AUTHORIZATION')
            user_id = None
            if token:
                try:
                    # 直接使用jwt_decode_handler
                    payload = jwt_decode_handler(token)
                    user_id = payload.get('user_id')
                except Exception:
                    pass

            # 创建模型记录
            model = YoloModel(
                name=os.path.splitext(model_file.name)[0],
                version='1.0',
                size=f'{round(model_file.size / 1024 / 1024, 2)}MB',
                file_path=relative_path,
                creator_id=user_id  # 设置创建者ID
            )
            model.save()

            return JsonResponse({'code': 200, 'message': '上传成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})


class ModelDownloadView(View):
    def get(self, request):
        """
        下载模型文件
        """
        try:
            model_id = request.GET.get('id')
            if not model_id:
                return JsonResponse({'code': 400, 'message': '缺少模型ID'})

            try:
                model = YoloModel.objects.get(id=model_id)
            except YoloModel.DoesNotExist:
                return JsonResponse({'code': 404, 'message': '模型不存在'})

            # 检查文件是否存在
            file_path = os.path.join(settings.BASE_DIR, 'model', os.path.basename(model.file_path))
            if not os.path.exists(file_path):
                return JsonResponse({'code': 404, 'message': '模型文件不存在'})

            # 返回文件流
            file = open(file_path, 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(model.file_path)}"'
            return response

        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})

class ModelActionView(View):
    def get(self, request):
        """
        获取模型详情
        """
        try:
            model_id = request.GET.get('id')
            # 原有的获取模型信息逻辑
            model = YoloModel.objects.get(id=model_id)
            return JsonResponse({
                'code': 200,
                'data': YoloModelSerializer(model).data
            })
        except YoloModel.DoesNotExist:
            return JsonResponse({'code': 404, 'message': '模型不存在'})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})

    def post(self, request):
        """
        保存或更新模型信息
        """
        try:
            data = json.loads(request.body)
            model_id = data.get('id')

            # 处理状态更新请求 (/modelYolo/status)
            if 'status' in data and len(data) == 2 and 'id' in data:
                try:
                    model = YoloModel.objects.get(id=model_id)
                    model.status = data['status']
                    model.save()
                    return JsonResponse({'code': 200, 'message': '状态更新成功'})
                except YoloModel.DoesNotExist:
                    return JsonResponse({'code': 404, 'message': '模型不存在'})

            # 处理保存请求 (/modelYolo/save)
            if model_id == -1:  # 新增模型
                # 获取当前用户ID
                token = request.META.get('HTTP_AUTHORIZATION')
                user_id = None
                if token:
                    try:
                        payload = jwt_decode_handler(token)
                        user_id = payload.get('user_id')
                    except Exception:
                        pass
                    
                model = YoloModel(
                    name=data.get('name'),
                    version=data.get('version'),
                    status=data.get('status', '正常'),
                    remark=data.get('remark'),
                    size='0MB',  # 新增时没有文件，设置默认值
                    file_path='',
                    creator_id=user_id  # 设置创建者ID
                )
            else:  # 更新模型
                try:
                    model = YoloModel.objects.get(id=model_id)
                    model.name = data.get('name', model.name)
                    model.version = data.get('version', model.version)
                    model.status = data.get('status', model.status)
                    model.remark = data.get('remark', model.remark)
                except YoloModel.DoesNotExist:
                    return JsonResponse({'code': 404, 'message': '模型不存在'})

            model.save()
            return JsonResponse({
                'code': 200,
                'message': '保存成功',
                'data': YoloModelSerializer(model).data
            })
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})

    def delete(self, request):
        """
        删除模型
        """
        try:
            data = json.loads(request.body)
            delete_ids = data.get('ids', [])
            action = data.get('action')
            
            if action != 'delete':
                return JsonResponse({'code': 400, 'message': '无效的操作类型'})
                
            if not delete_ids:
                return JsonResponse({'code': 400, 'message': '请选择要删除的模型'})

            models = YoloModel.objects.filter(id__in=delete_ids)
            if not models.exists():
                return JsonResponse({'code': 404, 'message': '未找到指定的模型'})

            # 删除文件
            for model in models:
                file_path = os.path.join(settings.MODELS_ROOT, os.path.basename(model.file_path))
                if os.path.exists(file_path):
                    os.remove(file_path)

            # 删除数据库记录
            models.delete()
            return JsonResponse({'code': 200, 'message': '删除成功'})
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'message': '无效的请求数据格式'})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': str(e)})
