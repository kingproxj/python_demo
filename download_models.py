# -*- coding: utf-8 -*-
import traceback
from multiprocessing import Process
import time
import urllib.request
import os

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


def logInfo(e):
    print("============================")
    print('错误类型是', e.__class__.__name__)
    print('错误明细是', e)
    result = traceback.format_exc()
    print(result)


def download():
    try:
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
                filename = code_url.split('=')[-1]
                print("开始下载", filename)
                # urllib.request.urlretrieve(code_url, filename, Schedule)
                try:
                    p = Process(target=urllib.request.urlretrieve, args=(code_url, filename, Schedule))
                    p_l.append(p)
                    p.start()
                    # urllib.request.urlretrieve(code_url, filename, Schedule)
                except ConnectionRefusedError as e:
                    result = traceback.format_exc()
                    print("下载模型和算法文件异常:",result)
                except Exception as e:
                    result = traceback.format_exc()
                    print("下载模型和算法文件异常:", result)
                    
            for p in p_l:
                p.join()

            print('主线程运行时间: %s' % (time.time() - start_time))

        if "ModelUri" in os.environ:
            modelUris = (os.getenv('ModelUri')).split(',')
            start_time = time.time()
            p_l = []
            for model_url in modelUris:
                filename = model_url.split('=')[-1]
                print("开始下载", filename)
                # urllib.request.urlretrieve(code_url, filename, Schedule)

                p = Process(target=urllib.request.urlretrieve, args=(model_url, filename, Schedule))
                p_l.append(p)
                p.start()

            for p in p_l:
                p.join()

            print('主线程运行时间: %s' % (time.time() - start_time))

    except AttributeError as e:
        return logInfo(e)
    except ModuleNotFoundError as e:
        return logInfo(e)
    except ImportError as e:
        return logInfo(e)
    except NameError as e:
        return logInfo(e)
    except KeyError as e:
        return logInfo(e)
    except IndexError as e:
        return logInfo(e)
    except LookupError as e:
        return logInfo(e)
    except SyntaxError as e:
        return logInfo(e)
    except StopIteration as e:
        return logInfo(e)
    except FloatingPointError as e:
        return logInfo(e)
    except OverflowError as e:
        return logInfo(e)
    except EOFError as e:
        return logInfo(e)
    except EnvironmentError as e:
        return logInfo(e)
    except IOError as e:
        return logInfo(e)
    except BaseException as e:
        return logInfo(e)
