import os
import yaml
from ultralytics import YOLO  # 导入YOLO模型
from QtFusion.path import abs_path
import torch

device = "0" if torch.cuda.is_available() else "cpu"

if __name__ == '__main__':  # 确保该模块被直接运行时才执行以下代码
    workers = 2
    batch = 10

    # data_name = "MetalCorrosion"
    # data_name = "beam_bottom"
    data_name = "data"
    data_path = abs_path(f'datasets/{data_name}/{data_name}.yaml', path_type='current')  # 数据集的yaml的绝对路径
    unix_style_path = data_path.replace(os.sep, '/')

    # 获取目录路径
    directory_path = os.path.dirname(unix_style_path)
    # 读取YAML文件，保持原有顺序
    with open(data_path, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    # 修改path项
    if 'path' in data:
        data['path'] = directory_path
        # 将修改后的数据写回YAML文件
        with open(data_path, 'w') as file:
            yaml.safe_dump(data, file, sort_keys=False)

    # 加载训练好的模型
    model = YOLO(model=f'runs/detect/train_v8_{data_name}/weights/best.pt', task='detect')  # 加载训练好的YOLOv8模型

    # 开始验证模型
    results = model.val(
        data=data_path,  # 指定验证数据的配置文件路径
        device=device,  # 自动选择进行验证
        workers=workers,  # 指定使用2个工作进程加载数据
        imgsz=640,  # 指定输入图像的大小为640x640
        name='val_v8_' + data_name  # 指定验证任务的名称
    )

    print(results)  # 打印验证结果
