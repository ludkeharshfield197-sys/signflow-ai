import os
import sys
import django

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_project.settings.dev")
django.setup()

# 导入必要的模块
import uvicorn

if __name__ == "__main__":
    # 从命令行获取端口参数，默认为8002
    port = 8002
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"无效的端口号: {sys.argv[1]}，使用默认端口8002")
    
    print(f"正在启动WebSocket服务器，端口: {port}")
    uvicorn.run("web_project.asgi:application", host="0.0.0.0", port=port)

    # python start_websocket.py 8002
