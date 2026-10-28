from django.core.management.base import BaseCommand
from daphne.server import Server
from channels.routing import get_default_application

class Command(BaseCommand):
    help = '在指定端口启动WebSocket服务器'

    def add_arguments(self, parser):
        parser.add_argument('--port', type=int, default=8002, help='指定端口号')
        parser.add_argument('--host', type=str, default='0.0.0.0', help='指定主机地址')

    def handle(self, *args, **options):
        port = options['port']
        host = options['host']
        
        self.stdout.write(self.style.SUCCESS(f'正在启动WebSocket服务器 {host}:{port}...'))
        
        application = get_default_application()
        server = Server(application, host=host, port=port)
        server.run() 