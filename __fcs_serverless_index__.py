# -*- coding: utf-8 -*-
import traceback
from multiprocessing import Process
import time
import urllib.request
import urllib.parse
import os

import fcs_status
import fcs_audit

import HandlerName
from t_snowflake import IdWorker

worker = IdWorker(1, 2, 0)

modelFiles = ""
if "ModelFile" in os.environ:
    modelFiles = os.environ["ModelFile"]
codeFiles = ""
if "CodeFile" in os.environ:
    codeFiles = os.environ["CodeFile"]

log_level = "debug"
if "log_level" in os.environ:
    log_level = os.environ["log_level"]


def logInfo(e, record_id, start_response):
    print("============================")
    print('错误类型是', e.__class__.__name__)
    print('错误明细是', e)
    result = traceback.format_exc()
    print(result)
    try:
        fcs_audit.recordAudit("铁笼异常", result, record_id, len(result))
    except KeyError as ke:
        print('ke错误类型是', ke.__class__.__name__)
        print('ke错误明细是', ke)
        traceback.print_exc()
    except BaseException as ke:
        print('ke错误类型是', ke.__class__.__name__)
        print('ke错误明细是', ke)
        traceback.print_exc()
    finally:
        print("============================")
        exceptStr = str(e.__class__.__name__) + ": " + str(e)
        responsebody = exceptStr
        if log_level == "debug":
            responsebody = str(result)
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [bytes(responsebody, encoding="utf8")]


def application(environ, start_response):
    try:
        # 创建fcs_status索引
        fcs_status.createStatusIndex()
        # 创建fcs_audit索引
        fcs_audit.createAuditIndex()

        # fcs_status.id == fcs_audit.id进行关联查询
        record_id = worker.get_id()
        # 记录启动状态
        fcs_status.recordStatus(record_id)
        params = environ['QUERY_STRING']
        print("origin environ['QUERY_STRING']: ", params)
        environ['QUERY_STRING'] = urllib.parse.unquote(params)
        print("unquote_params is ", environ['QUERY_STRING'])
        fcs_audit.recordAudit("铁笼启动", "参数: " + environ['QUERY_STRING'], record_id, len(environ["QUERY_STRING"]))
        # fcs_audit.recordAudit("加载模型", codeFiles, record_id)
        # fcs_audit.recordAudit("加载算法", codeFiles, record_id)

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
                fcs_audit.recordAudit("加载模型", "下载模型和算法文件" + filename, record_id, totalsize)
                print('%s当前下载进度：%d' % (filename, per))

        if "CodeUri" in os.environ:
            codeUris = (os.getenv('CodeUri')).split(',')
            start_time = time.time()
            # p_l = []
            for code_url in codeUris:
                filename = code_url.split('=')[-1]
                print("开始下载", filename)
                # fcs_audit.recordAudit("加载模型", "下载模型和算法文件" + filename, record_id)
                # urllib.request.urlretrieve(code_url, filename, Schedule)
                try:
                    # p = Process(target=urllib.request.urlretrieve, args=(code_url, filename, Schedule))
                    # p_l.append(p)
                    # p.start()
                    urllib.request.urlretrieve(code_url, filename, Schedule)
                except ConnectionRefusedError as e:
                    result = traceback.format_exc()
                    print("下载模型和算法文件异常:",result)
                    exceptStr = str(e.__class__.__name__) + ": " + str(e)
                    if log_level == "debug":
                        fcs_audit.recordAudit("铁笼异常", "下载模型和算法文件异常: " + str(result), record_id, len(result))
                    else:
                        fcs_audit.recordAudit("铁笼异常", "下载模型和算法文件异常: " + exceptStr, record_id, len(exceptStr))
                except Exception as e:
                    result = traceback.format_exc()
                    print("下载模型和算法文件异常:", result)
                    exceptStr = str(e.__class__.__name__) + ": " + str(e)
                    if log_level == "debug":
                        fcs_audit.recordAudit("铁笼异常", "下载模型和算法文件异常: " + str(result), record_id, len(str(result)))
                    else:
                        fcs_audit.recordAudit("铁笼异常", "下载模型和算法文件异常: " + exceptStr, record_id, len(exceptStr))

            # for p in p_l:
            #     p.join()

            print('主线程运行时间: %s' % (time.time() - start_time))

        if "ModelUri" in os.environ:
            modelUris = (os.getenv('ModelUri')).split(',')
            start_time = time.time()
            p_l = []
            for model_url in modelUris:
                filename = model_url.split('=')[-1]
                print("开始下载", filename)
                # fcs_audit.recordAudit("加载模型", "下载模型和算法文件" + filename, record_id)
                # urllib.request.urlretrieve(code_url, filename, Schedule)

                p = Process(target=urllib.request.urlretrieve, args=(model_url, filename, Schedule))
                p_l.append(p)
                p.start()

            for p in p_l:
                p.join()

            print('主线程运行时间: %s' % (time.time() - start_time))

        try:
            result = HandlerName.FunctionName(environ, start_response)
            if result:
                result = str(result[0], encoding="utf-8")
            fcs_audit.recordAudit("铁笼输出", str(result), record_id, len(str(result)))
        except Exception as e:
            trans_result = traceback.format_exc()
            print("下载模型和算法文件异常:", trans_result)
            exceptStr = str(e.__class__.__name__) + ": " + str(e)
            if log_level == "debug":
                fcs_audit.recordAudit("铁笼输出", "计算异常: " + str(trans_result), record_id, len(str(trans_result)))
            else:
                fcs_audit.recordAudit("铁笼输出", "计算异常: " + exceptStr, record_id, len(exceptStr))
            responsebody = str(trans_result)
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [bytes(responsebody, encoding="utf8")]
        finally:
            fcs_audit.recordAudit("铁笼销毁", "", record_id, 0)
            # 更新为销毁状态
            fcs_status.recordStatus(record_id)
        return result
    except AttributeError as e:
        return logInfo(e, record_id, start_response)
    except ModuleNotFoundError as e:
        return logInfo(e, record_id, start_response)
    except ImportError as e:
        return logInfo(e, record_id, start_response)
    except NameError as e:
        return logInfo(e, record_id, start_response)
    except KeyError as e:
        return logInfo(e, record_id, start_response)
    except IndexError as e:
        return logInfo(e, record_id, start_response)
    except LookupError as e:
        return logInfo(e, record_id, start_response)
    except SyntaxError as e:
        return logInfo(e, record_id, start_response)
    except StopIteration as e:
        return logInfo(e, record_id, start_response)
    except FloatingPointError as e:
        return logInfo(e, record_id, start_response)
    except OverflowError as e:
        return logInfo(e, record_id, start_response)
    except EOFError as e:
        return logInfo(e, record_id, start_response)
    except EnvironmentError as e:
        return logInfo(e, record_id, start_response)
    except IOError as e:
        return logInfo(e, record_id, start_response)
    except BaseException as e:
        return logInfo(e, record_id, start_response)
    # finally:
    #     print("=======")
    #     print(result)
    #     print("=======")
    #     responsebody = str(result)
    #     start_response('200 OK', [('Content-Type', 'application/json')])
    #     return [bytes(responsebody, encoding="utf8")]
