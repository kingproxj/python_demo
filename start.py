import urllib.request
import os

from multiprocessing import Process
import time
# 从wsgiref模块导入:
from wsgiref.simple_server import make_server
# 导入我们自己编写的application函数:
from __fcs_serverless_index__ import application

#os.environ["Handler"]="index.application"
#os.environ['CodeUri'] = 'https://raw.githubusercontent.com/kingproxj/python_demo/master/replace.sh,https://raw.githubusercontent.com/kingproxj/python_demo/start.sh'

def Schedule(blocknum, blocksize, totalsize):
    '''
    :param blocknum: 已经下载的数据块
    :param blocksize: 数据块的大小
    :param totalsize: 远程文件的大小
    :return:
    '''
    per = 100.0*blocknum*blocksize/totalsize
    if per > 100:
        per = 100
        print('%s当前下载进度：%d' % (filename, per))

if "CodeUri" in os.environ:
    codeUris = (os.getenv('CodeUri')).split(',')
    start_time=time.time()
    p_l=[]
    for code_url in codeUris:
        filename = code_url.split('/')[-1]
        print("开始下载", filename)
        #urllib.request.urlretrieve(code_url, filename, Schedule)

        p=Process(target=urllib.request.urlretrieve,args=(code_url, filename, Schedule))
        p_l.append(p)
        p.start()

    for p in p_l:
        p.join()

    print('主线程运行时间: %s'%(time.time()-start_time))

print("开始执行replace.sh")
repval = os.system('sh replace.sh')
print("执行结果为",repval)
#if repval == 0: 
    #print("开始执行server.py") #启动服务
    #os.system('python3 {}'.format("server.py"))

# 创建一个服务器，IP地址为空，端口是8000，处理函数是application:
httpd = make_server('', 8000, application)
print('Serving HTTP on port 8000...')
# 开始监听HTTP请求:
httpd.serve_forever()
