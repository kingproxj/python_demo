# -*- coding: utf-8 -*-

# 从wsgiref模块导入:
from wsgiref.simple_server import make_server
# 导入我们自己编写的application函数:
from __fcs_serverless_index__ import application
import fcs_status

#os.environ["Handler"]="index.application"
#os.environ['CodeUri'] = 'https://raw.githubusercontent.com/kingproxj/python_demo/master/replace.sh,https://raw.githubusercontent.com/kingproxj/python_demo/start.sh'

# 创建一个服务器，IP地址为空，端口是8000，处理函数是application:
httpd = make_server('', 8000, application)
print('Serving HTTP on port 8000...')
# 开始监听HTTP请求:
httpd.serve_forever()
