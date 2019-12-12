import urllib.request
import os

from multiprocessing import Process
import time

#os.environ["Handler"] = "index.application"
#os.environ['CodeUri'] = 'http://10.221.128.170:30885/download/change_info.csv,https://raw.githubusercontent.com/kingproxj/fcs/master/server.py,https://raw.githubusercontent.com/kingproxj/fcs/master/index.py,https://raw.githubusercontent.com/kingproxj/fcs/master/replace.sh,https://raw.githubusercontent.com/kingproxj/fcs/master/Python3.7/start.sh,https://raw.githubusercontent.com/kingproxj/fcs/master/server.py'

def Schedule(blocknum, blocksize, totalsize):
    '''
    :param blocknum: 已经下载的数据块
    :param blocksize: 数据块的大小
    :param totalsize: 远程文件的大小
    :return:
    '''
    per = 100.0 * blocknum * blocksize / totalsize
    if per > 100:
        per = 100
        print('%s当前下载进度：%d' % (filename, per))


if "CodeUri" in os.environ:
    codeUris = (os.getenv('CodeUri')).split(',')
    start_time = time.time()
    p_l = []
    for code_url in codeUris:
        filename = code_url.split('/')[-1]
        print("开始下载", filename)
        # urllib.request.urlretrieve(code_url, filename, Schedule)

        p = Process(target=urllib.request.urlretrieve, args=(code_url, filename, Schedule))
        p_l.append(p)
        p.start()

    for p in p_l:
        p.join()

    print('主线程运行时间: %s' % (time.time() - start_time))

lst = os.listdir(os.getcwd())  # 获取当前目录下所有的文件名
for c in lst:
    if os.path.isfile(c) and c.endswith('.sh') and c.find("replace.sh") == 0:
        print("开始执行", c)  # 查看文件
        os.system('sh {}'.format(c))  # 执行replace.sh
    if os.path.isfile(c) and c.endswith('.sh') and c.find("start.sh") == 0:
        co = "sh " + c
        print("开始执行", co)  # 下载模型
        val = os.system(co)
        print("执行结果为", val)
    if os.path.isfile(c) and c.endswith('.py') and c.find("server.py") == 0:
        print("开始执行", c)  # 启动服务
        os.system('python {}'.format(c))

print("===")
