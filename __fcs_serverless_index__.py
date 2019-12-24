# -*- coding: utf-8 -*-
from multiprocessing import Process
import time
import urllib.request
import os

import fcs_status
import fcs_audit

import HandlerName

modelFiles = ""
if "ModelFile" in os.environ:
    modelFiles = os.environ["ModelFile"]
codeFiles = ""
if "CodeFile" in os.environ:
    codeFiles = os.environ["CodeFile"]
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
            fcs_audit.recordAudit("铁笼启动", "下载模型和算法文件" + filename)
            # urllib.request.urlretrieve(code_url, filename, Schedule)

            p = Process(target=urllib.request.urlretrieve, args=(code_url, filename, Schedule))
            p_l.append(p)
            p.start()

        for p in p_l:
            p.join()

        print('主线程运行时间: %s' % (time.time() - start_time))

    if "ModelUri" in os.environ:
        modelUris = (os.getenv('ModelUri')).split(',')
        start_time = time.time()
        p_l = []
        for model_url in modelUris:
            filename = model_url.split('/')[-1]
            print("开始下载", filename)
            fcs_audit.recordAudit("铁笼启动", "下载模型和算法文件" + filename)
            # urllib.request.urlretrieve(code_url, filename, Schedule)

            p = Process(target=urllib.request.urlretrieve, args=(model_url, filename, Schedule))
            p_l.append(p)
            p.start()

        for p in p_l:
            p.join()

        print('主线程运行时间: %s' % (time.time() - start_time))

    params = environ['QUERY_STRING']
    fcs_audit.recordAudit("输入参数", params)
    fcs_audit.recordAudit("加载模型", codeFiles)
    # fcs_audit.recordAudit("加载算法", codeFiles)
    result = HandlerName.FunctionName(environ, start_response)
    fcs_audit.recordAudit("铁笼输出", result)
    # 更新为销毁状态
    fcs_status.recordStatus()
    return result
