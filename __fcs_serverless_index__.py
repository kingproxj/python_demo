# -*- coding: utf-8 -*-
import traceback
from multiprocessing import Pool
import time
import urllib.request
import urllib.parse
import os

import fcs_status
import fcs_audit
from logger import logger

from t_snowflake import IdWorker

worker = IdWorker(1, 2, 0)

modelFiles = ""
if "ModelFile" in os.environ:
    modelFiles = os.environ["ModelFile"]
codeFiles = ""
if "CodeFile" in os.environ:
    codeFiles = os.environ["CodeFile"]

log_level = "DEBUG"
if "log_level" in os.environ:
    log_level = os.environ["log_level"]

audit_records = []

def logInfo(e, record_id, start_response):
    logger.debug('错误类型是%s', e.__class__.__name__)
    logger.debug('错误明细是%s', e)
    result = traceback.format_exc()
    logger.debug(result)
    try:
        global audit_records
        audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼异常", result, record_id, len(result)))
    except KeyError as ke:
        logger.exception("Exception occurred")
        traceback.logger.debug_exc()
    except BaseException as ke:
        logger.exception("Exception occurred")
        traceback.logger.debug_exc()
    finally:
        exceptStr = str(e.__class__.__name__) + ": " + str(e)
        responsebody = exceptStr
        if log_level == "DEBUG":
            responsebody = str(result)
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [bytes(responsebody, encoding="utf8")]

def downloadFile(code_url, filename, record_id):
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
            logger.debug('%s当前下载进度：%d' % (filename, per))
    try:
        filepath, httpMessage = urllib.request.urlretrieve(code_url, filename, Schedule)
    except Exception as e:
        logger.exception("下载异常")
        traceback.logger.debug_exc()
    return filepath, httpMessage["Content-Length"]


def application(environ, start_response):
    try:
        # 创建fcs_status索引
        fcs_status.create_status_index()
        # 创建fcs_audit索引
        fcs_audit.create_audit_index()

        # fcs_status.id == fcs_audit.id进行关联查询
        record_id = worker.get_id()
        # 记录启动状态
        fcs_status.record_status(record_id)
        params = environ['QUERY_STRING']
        logger.debug("origin environ['QUERY_STRING']: %s", params)
        environ['QUERY_STRING'] = urllib.parse.unquote(params)
        logger.debug("unquote_params is %s", environ['QUERY_STRING'])
        global audit_records
        audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼启动", "参数: " + environ['QUERY_STRING'], record_id, len(environ["QUERY_STRING"])))
        # fcs_audit.record_audit("加载模型", codeFiles, record_id)
        # fcs_audit.record_audit("加载算法", codeFiles, record_id)

        pl = Pool(10)  # 进程池中从无到有创建10个进程,以后一直是这10个进程在执行任务
        res_l = []

        if "CodeUri" in os.environ:
            codeUris = str(os.getenv('CodeUri')).split(',')
            if "ModelUri" in os.environ:
                codeUris.extend(str(os.getenv('ModelUri')).split(','))
            start_time = time.time()
            # p_l = []
            for code_url in codeUris:
                filename = code_url.split('=')[-1]
                logger.debug("开始下载%s", filename)
                # fcs_audit.record_audit("加载模型", "下载模型和算法文件" + filename, record_id)
                # urllib.request.urlretrieve(code_url, filename, Schedule)
                try:
                    # p = Process(target=urllib.request.urlretrieve, args=(code_url, filename, Schedule))
                    # p_l.append(p)
                    # p.start()

                    # urllib.request.urlretrieve(code_url, filename, Schedule)

                    res = pl.apply_async(downloadFile,
                                         args=(code_url, filename, record_id))  # 异步运行，根据进程池中有的进程数，每次最多3个子进程在异步执行
                    # 返回结果之后，将结果放入列表，归还进程，之后再执行新的任务
                    # 需要注意的是，进程池中的三个进程不会同时开启或者同时结束
                    # 而是执行完一个就释放一个进程，这个进程就去接收新的任务。
                    data_size = res.get()[1]
                    audit_records.append(
                        fcs_audit.assemble_audit_record_with_index("加载模型", "下载模型和算法文件" + filename, record_id,
                                                                   int(data_size)))
                    res_l.append(res)

                except ConnectionRefusedError as e:
                    result = traceback.format_exc()
                    logger.exception("下载模型和算法文件异常")
                    except_str = str(e.__class__.__name__) + ": " + str(e)
                    if log_level == "DEBUG":
                        audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼异常", "下载模型和算法文件异常: " + str(result), record_id, len(result)))
                    else:
                        audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼异常", "下载模型和算法文件异常: " + except_str, record_id, len(except_str)))
                except Exception as e:
                    result = traceback.format_exc()
                    logger.exception("下载模型和算法文件异常")
                    except_str = str(e.__class__.__name__) + ": " + str(e)
                    if log_level == "DEBUG":
                        audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼异常", "下载模型和算法文件异常: " + str(result), record_id, len(str(result))))
                    else:
                        audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼异常", "下载模型和算法文件异常: " + except_str, record_id, len(except_str)))

            # for p in p_l:
            #     p.join()

            # logger.debug('主线程运行时间: %s' % (time.time() - start_time))

        # 异步apply_async用法：如果使用异步提交的任务，主进程需要使用jion，等待进程池内任务都处理完，然后可以用get收集结果
        # 否则，主进程结束，进程池可能还没来得及执行，也就跟着一起结束了
        pl.close()
        pl.join()
        for res in res_l:
            # 使用get来获取apply_aync的结果,如果是apply,则没有get方法,因为apply是同步执行,立刻获取结果,也根本无需get
            logger.debug("res.get is %s", res.get())

        logger.debug('主线程运行时间: %s' % (time.time() - start_time))

        try:
            defaultHandler = "HandlerName"
            mod = __import__(defaultHandler)
            result = mod.FunctionName(environ, start_response)
            if result:
                export_result = str(result[0], encoding="utf-8")
            audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼输出", str(export_result), record_id, len(str(result))))
        except Exception as e:
            trans_result = traceback.format_exc()
            logger.exception("计算异常")
            except_str = str(e.__class__.__name__) + ": " + str(e)
            if log_level == "DEBUG":
                audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼输出", "计算异常: " + str(trans_result), record_id, len(str(trans_result))))
            else:
                audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼输出", "计算异常: " + except_str, record_id, len(except_str)))
            responsebody = str(trans_result)
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [bytes(responsebody, encoding="utf8")]
        finally:
            audit_records.append(fcs_audit.assemble_audit_record_with_index("铁笼销毁", "", record_id, 0))
            logger.debug("audit_records is %s", audit_records)
            fcs_audit.bulk_record(audit_records)
            # 更新为销毁状态
            fcs_status.record_status(record_id)
        logger.debug("===audit_records is===%s", audit_records)
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
    #     logger.debug("=======")
    #     logger.debug(result)
    #     logger.debug("=======")
    #     responsebody = str(result)
    #     start_response('200 OK', [('Content-Type', 'application/json')])
    #     return [bytes(responsebody, encoding="utf8")]
