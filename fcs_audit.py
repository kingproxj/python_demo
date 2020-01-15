# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from t_snowflake import IdWorker
from logger import logger

worker = IdWorker(1, 2, 0)
esHost = "117.73.3.232:31103"
if "ES_SERVER_HOST" in os.environ:
    esHost = os.environ["ES_SERVER_HOST"]
es = Elasticsearch([esHost])
es_audit_index = "fcs_audit"
if "es_audit_index" in os.environ:
    es_audit_index = os.environ["es_audit_index"]


def create_audit_index():
    """
    数据铁笼的审计信息，每个铁笼的各个阶段的详细情况，加载参数情况,在区块链上，查询时，同一个铁笼的按照created_time_ms排序
    :return:
    """
    res = es.indices.exists(index=es_audit_index)
    logger.debug("%s es.indices.exists is %s", es_audit_index, res)
    if not res:
        # 创建fcs_audit索引
        mappings = {
            "mappings": {
                "doc": {
                    "properties": {
                        "detail": {
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
                        "id": {
                            "type": "keyword"
                        },
                        "service_id": {
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
                        },
                        "ops": {
                            "type": "keyword"
                        },
                        "data_size": {
                            "type": "long"
                        },
                        "block_id": {
                            "type": "keyword"
                        },
                        "block_number": {
                            "type": "long"
                        },
                        "created_time_ms": {
                            "type": "long"
                        },
                        "status": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
        res = es.indices.create(index=es_audit_index, body=mappings)
        logger.debug(res)


def record_audit(operations, detail, record_id=None, date_size=None):
    """
    记录启动铁笼日志
    """
    action = assemble_audit_record(operations, detail, record_id, date_size)
    logger.debug("record is %s", action)
    res = es.index(index=es_audit_index, doc_type="doc", body=action)
    logger.debug("record result is %s", res)


def bulk_record(actions):
    logger.debug("bulk_record actions is %s", actions)
    res, _ = bulk(es, actions, index=es_audit_index, raise_on_error=True)
    logger.debug("bulk_record res is %d", res)


def assemble_audit_record_with_index(operations, detail, record_id=None, date_size=None):
    action = assemble_audit_record(operations, detail, record_id, date_size)
    action_with_index = {
        "_index": es_audit_index,
        "_type": "doc",
        "_source": action
    }
    logger.debug("action_with_index is %s", action_with_index)
    return action_with_index


def assemble_audit_record(operations, detail, record_id=None, date_size=None):
    """
    组装记录启动铁笼日志报文
    """
    if record_id is None:
        record_id = worker.get_id()
        logger.debug("id is %s", record_id)
    if date_size is None:
        date_size = 0
    logger.debug("operation is %s", operations)
    if operations == "":
        logger.debug("operations is none, return")
        return

    # res = es.indices.exists(index=es_audit_index)
    # 默认已创建es_audit_index索引
    res = True
    if not res:
        # 创建索引,建立mapping索引
        logger.debug("请先创建索引fcs_audit")
    else:
        op_status = "成功"
        if "异常" in operations or "异常" in detail:
            op_status = "失败"
        recordId = os.environ["IS_RECORD"]
        service_id = os.environ["HOSTNAME"]
        if "service_id" in os.environ:
            service_id = os.environ['service_id']
        handler = os.environ["Handler"]
        runtime = os.environ["Runtime"]
        serverName = os.environ["SERVER_NAME"]
        if "service_name_cn" in os.environ:
            serverName = os.environ["service_name_cn"]
        now = datetime.now()
        dt = time.time()
        created_time_ms = int(round(dt * 1000))
        logger.debug(now.strftime("%Y-%m-%d %H:%M:%S"))
        createTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(dt)))
        # 更新数据
        action = {
            "id": record_id,
            "service_id": service_id,
            "service_name": serverName,
            "ops": operations,
            "block_id": "736473430",
            "block_number": 255323,
            "data_size": date_size,
            "detail": detail,
            "created_time": createTime,
            "created_time_ms": created_time_ms,
            "status": op_status
        }
        logger.debug("record is %s", action)
        # res = es.index(index=es_audit_index, doc_type="doc", body=action)
        # logger.debug("record result is %s", res)
        return action


if __name__ == '__main__':
    environ = {
        "QUERY_STRING": "test=a"
    }
    create_audit_index()
    # id = worker.get_id()
    # logger.debug(id)
