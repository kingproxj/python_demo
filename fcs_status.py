# -*- coding: utf-8 -*-
import os
import time
import traceback
from datetime import datetime

import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from t_snowflake import IdWorker
from logger import logger

worker = IdWorker(1, 2, 0)

esHost = "117.73.3.232:31103"
if "ES_SERVER_HOST" in os.environ:
    esHost = os.environ["ES_SERVER_HOST"]
es = Elasticsearch([esHost])
es_status_index = "fcs_status"
if "es_status_index" in os.environ:
    es_status_index = os.environ["es_status_index"]


def create_status_index():
    """
    记录启动铁笼日志，数据铁笼的运行监控信息，状态信息，由后台写入ES中，其文档id就是ids_id
    """
    res = es.indices.exists(index=es_status_index)
    logger.debug("%s es.indices.exists is %s", es_status_index, res)
    if not res:
        # 创建索引,建立mapping索引
        mappings = {
            "mappings": {
                "doc": {
                    "properties": {
                        "company_name": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "created_time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss"

                        },
                        "destroy_time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss"
                        },
                        "id": {
                            "type": "keyword"
                        },
                        "live_time": {
                            "type": "long"
                        },
                        "request_id": {
                            "type": "keyword"
                        },
                        "service_id": {
                            "type": "keyword"
                        },
                        "user_id": {
                            "type": "keyword"
                        },
                        "blockchain": {
                            "type": "keyword"
                        },
                        "status": {
                            "type": "keyword"
                        },
                        "service_name": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                }
            }
        }
        logger.debug(mappings)
        res = es.indices.create(index=es_status_index, body=mappings)
        logger.debug("es.indices.create result is %s", res)


def record_status(record_id=None):
    """
    记录启动铁笼日志，数据铁笼的运行监控信息，状态信息，由后台写入ES中，其文档id就是ids_id
    """
    # 铁笼启动是否已经记录
    if record_id is None:
        record_id = worker.get_id()
        logger.debug("id is %s", record_id)
    isRecorded = os.environ["IS_RECORD"]
    service_id = os.environ["HOSTNAME"]
    if "service_id" in os.environ:
        service_id = os.environ['service_id']
    handler = os.environ["Handler"]
    runtime = os.environ["Runtime"]
    serverName = os.environ["SERVER_NAME"]
    if "service_name_cn" in os.environ:
        serverName = os.environ["service_name_cn"]
    content = "启动铁笼" + service_id
    now = datetime.now()
    logger.debug(now.strftime("%Y-%m-%d %H:%M:%S"))
    dt = time.time()
    nowFormat = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(dt)))
    user_id = os.environ["creator"]
    if isRecorded == "0":
        # 插入数据
        action = {
            "id": record_id,
            "service_id": service_id,
            "service_name": serverName,
            "request_id": "",
            "user_id": user_id,
            "company_name": "",
            "live_time": 0,
            "destroy_time": None,
            "created_time": nowFormat,
            "status": "运行中",
            "blockchain": "数安链"
        }
        res = es.index(index=es_status_index, doc_type="doc", body=action)
        logger.debug("insert status result: %s", res)
        # {'_index': 'fcs', '_type': 'type_doc', '_id': 'z4dbDW8BtULaBa6qlsZO', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 2, 'failed': 0}, '_seq_no': 0, '_primary_term': 1}
        if res["result"] == "created":
            os.environ["IS_RECORD"] = res["_id"]
            logger.debug("IS_RECORD is %s", os.environ["IS_RECORD"])
    else:
        # # 根据关键词查找
        # doc = {
        #     "query": {
        #         "match": {
        #             # "_id": "jId_RW8BtULaBa6q8cmB"
        #             "_id": isRecorded
        #         }
        #     }
        # }
        # res = es.search(index=es_status_index, body=doc)
        # # {'took': 97, 'timed_out': False, '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0}, 'hits': {'total': 1, 'max_score': 1.0, 'hits': [{'_index': 'fcs_status', '_type': 'doc', '_id': 'jId_RW8BtULaBa6q8cmB', '_score': 1.0, '_source': {'id': 1210409175465730048, 'service_id': 'aa527f36-da1c-4406-baa6-d62f1943c9c3', 'service_name': '铁笼调用联通测试', 'request_id': '', 'user_id': 'a6837cf7-704a-41bd-a38f-fbfb8c4841bb', 'company_name': '', 'live_time': 0, 'destroy_time': '2019-12-27 11:56:52', 'created_time': '2019-12-27 11:56:50', 'status': '已销毁', 'blockchain': '数安链'}}]}}
        # # {'took': 14, 'timed_out': False, '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0}, 'hits': {'total': 0, 'max_score': None, 'hits': []}}
        # created_time = nowFormat
        # if res["hits"]["total"] > 0:
        #     created_time = res["hits"]["hits"][0]["_source"]["created_time"]
        # logger.debug("created_time is %s", created_time)
        # created_time_ms = int(round(time.mktime(time.strptime(created_time, "%Y-%m-%d %H:%M:%S"))) * 1000)
        # logger.debug("created_time_ms is %s", created_time_ms)
        # destroy_time_ms = int(round(dt*1000))
        # logger.debug("destroy_time_ms is %s", destroy_time_ms)
        # live_time_ms = destroy_time_ms - created_time_ms
        # logger.debug("live_time_ms is %s", live_time_ms)
        # # 更新数据
        # action = {
        #     "doc": {
        #         # "id": isRecorded,
        #         # "service_id": hostName,
        #         # "service_name": serverName,
        #         # "request_id": "",
        #         # "user_id": user_id,
        #         # "company_name": "",
        #         "live_time": live_time_ms,
        #         "destroy_time": nowFormat,
        #         # "created_time": createTime,
        #         "status": "已销毁",
        #         "blockchain": "数安链"
        #     }
        # }
        # logger.debug("update status %s", os.environ["IS_RECORD"])
        # res = es.update(index=es_status_index, id=isRecorded, doc_type="doc", body=action)
        # logger.debug("es.update result is %s", res)

        # 根据id查询
        try:
            res = es.get(index=es_status_index, doc_type="doc", id=isRecorded)
            # {'_index': 'fcs_status', '_type': 'doc', '_id': 'jId_RW8BtULaBa6q8cmB', '_version': 2, 'found': True, '_source': {'id': 1210409175465730048, 'service_id': 'aa527f36-da1c-4406-baa6-d62f1943c9c3', 'service_name': '铁笼调用联通测试', 'request_id': '', 'user_id': 'a6837cf7-704a-41bd-a38f-fbfb8c4841bb', 'company_name': '', 'live_time': 0, 'destroy_time': '2019-12-27 11:56:52', 'created_time': '2019-12-27 11:56:50', 'status': '已销毁', 'blockchain': '数安链'}}
            created_time = res["_source"]["created_time"]
            logger.debug("created_time is %s", created_time)
            created_time_ms = int(round(time.mktime(time.strptime(created_time, "%Y-%m-%d %H:%M:%S"))) * 1000)
            logger.debug("created_time_ms is %s", created_time_ms)
            destroy_time_ms = int(round(dt * 1000))
            logger.debug("destroy_time_ms is %s", destroy_time_ms)
            live_time_ms = destroy_time_ms - created_time_ms
            logger.debug("live_time_ms is %s", live_time_ms)
            # 更新数据
            action = {
                "doc": {
                    # "id": isRecorded,
                    # "service_id": hostName,
                    # "service_name": serverName,
                    # "request_id": "",
                    # "user_id": user_id,
                    # "company_name": "",
                    "live_time": live_time_ms,
                    "destroy_time": nowFormat,
                    # "created_time": createTime,
                    "status": "已销毁",
                    "blockchain": "数安链"
                }
            }
            logger.debug("update status %s", os.environ["IS_RECORD"])
            res = es.update(index=es_status_index, id=isRecorded, doc_type="doc", body=action)
            # logger.debug("es.update result is", res)
            logger.debug("status_index res is %s", res)
        except elasticsearch.exceptions.NotFoundError as e:
            logger.debug('错误类型是%s', e.__class__.__name__)
            logger.debug('错误明细是%s', e)
            result = traceback.format_exc()
            logger.debug(result)
        except Exception as e:
            logger.debug('错误类型是%s', e.__class__.__name__)
            logger.debug('错误明细是%s', e)
            result = traceback.format_exc()
            logger.debug(result)


if __name__ == '__main__':
    # environ = {
    #     "QUERY_STRING": "test=a"
    # }
    record_status()
    # id = worker.get_id()
    # logger.debug(id)
