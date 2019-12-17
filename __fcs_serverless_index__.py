# -*- coding: utf-8 -*-
from multiprocessing import Process
import time
import urllib.request
import os

import fcs_status
import fcs_audit

import HandlerName


modules = os.environ["CodeFile"]
def application(environ, start_response):
    # 记录启动状态
    fcs_status.recordStatus()
    print("environ['QUERY_STRING']")

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
            fcs_audit.RecordAudit("铁笼启动", "下载模型" + filename)
            # urllib.request.urlretrieve(code_url, filename, Schedule)

            p = Process(target=urllib.request.urlretrieve, args=(code_url, filename, Schedule))
            p_l.append(p)
            p.start()

        for p in p_l:
            p.join()

        print('主线程运行时间: %s' % (time.time() - start_time))

    params = environ['QUERY_STRING']
    fcs_audit.RecordAudit("输入参数", params)
    fcs_audit.RecordAudit("加载模型", modules)
    result = HandlerName.FunctionName(environ, start_response)
    fcs_audit.RecordAudit("铁笼输出", result)
    # 更新为销毁状态
    fcs_status.recordStatus()
    return result
