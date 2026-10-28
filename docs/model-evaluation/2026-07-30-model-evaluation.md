# SignFlow AI 本地模型评测报告

评测日期：2026-07-30  
评测原则：仅使用现有权重进行推理，不训练、不微调、不改写 `.pt` 文件。

## 1. 评测环境

- 处理器：13th Gen Intel Core i7-13700H，14 核 / 20 线程
- 推理设备：CPU
- Python：3.12.3
- PyTorch：2.13.0+cpu
- Ultralytics：8.3.80
- 输入尺寸：640×640
- 检测评测批量：16
- 产品链路参数：置信度阈值 0.45，IoU 阈值 0.50

## 2. 检测指标

| 模型 | 语言 / 类别 | 数据集 | 样本 / 实例 | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---:|---:|---:|---:|---:|
| `ASl-v8.pt` | ASL / 80 类 | ASL-80 带框保留验证集 | 2,053 / 2,085 | 97.63% | 98.81% | 98.94% | 76.94% |
| `csl.pt` | CSL / 37 类 | CSL-37 带框独立测试集 | 347 / 346 | 99.63% | 99.20% | 99.49% | 84.29% |

ASL 数据目录仅提供 `train` 与 `val`，因此 ASL 检测指标必须标注为训练期间可见的验证集结果，不能表述为外部独立盲测。CSL 使用仓库 `data.yaml` 明确声明的 `test` split；现有文件仍不足以证明不同 split 的采集主体完全独立。

## 3. 产品链路回归与性能

| 模型 | 回归素材 | 标签 Precision / Recall | 单张平均延迟 | 视频处理速度 |
|---|---:|---:|---:|---:|
| ASL-80 | 10 个（5 图、4 视频、1 负样例） | 100% / 100% | 83.15 ms | 11.75 FPS |
| CSL-37 | 5 个（2 图、3 视频） | 100% / 100% | 76.83 ms | 11.48 FPS |

产品链路回归集用于确认图片、视频、标签映射和负样例处理是否真实可用。它规模很小，且 ASL 的 5 张图片来自保留验证集，不能用 100% 回归通过率替代总体模型准确率。

## 4. 复测方法

检测指标由现有权重调用 `YOLO.val` 得出：

```powershell
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('web_project/model/csl.pt').val(data='<CSL YAML>', split='test', imgsz=640, batch=16, device='cpu')"
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('web_project/model/ASl-v8.pt').val(data='<ASL YAML>', split='val', imgsz=640, batch=16, device='cpu')"
```

图片延迟、视频 FPS 与产品回归指标可重复执行：

```powershell
.\.venv\Scripts\python.exe web_project\scripts\benchmark_model_cards.py
```

评测结果已同步到 `inference/evaluation_cards.json`，模型中心从后端模型记录读取，不再显示未配置占位值。

## 5. 已知能力边界

- ASL 模型只覆盖 80 个餐饮与公共服务词汇；CSL 模型只覆盖 37 个固定动作。
- 当前模型是目标检测式词汇识别，不等同于开放词汇、连续手语翻译或自然语言语法还原。
- 光线、遮挡、手部出框、多人同时出现、动作速度与拍摄角度会影响结果。
- 回归素材规模小，不能推导不同人群、设备和真实场景中的总体表现。
- CPU 延迟是本机实测，不代表移动端、GPU 或云端部署性能。
- 识别结果用于沟通辅助，关键内容应由沟通双方确认。
