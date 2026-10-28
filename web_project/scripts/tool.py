import cv2


def get_video_info(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {file_path}")
        return

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)  # 帧率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 高度
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
    duration = frame_count / fps  # 时长（秒）
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))  # 编码格式
    codec = (
        chr(fourcc & 0xFF)
        + chr((fourcc >> 8) & 0xFF)
        + chr((fourcc >> 16) & 0xFF)
        + chr((fourcc >> 24) & 0xFF)
    )

    print(f"视频文件: {file_path}")
    print(f"编码格式: {codec}")
    print(f"分辨率: {width}x{height}")
    print(f"帧率: {fps} fps")
    print(f"总帧数: {frame_count}")
    print(f"时长: {duration:.2f} 秒")

    cap.release()


# 示例调用

get_video_info("../media/videos/ljy.mp4")
get_video_info("../media/videos/result_ljy.mp4")
get_video_info("../media/videos/result_ljy_m4Au2nb.mp4")
