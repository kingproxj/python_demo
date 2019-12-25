# -*- coding: utf-8 -*-
import os
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from t_snowflake import IdWorker

worker = IdWorker(1, 2, 0)
esHost = "117.73.3.232:31103"
if "ES_SERVER_HOST" in os.environ:
    esHost = os.environ["ES_SERVER_HOST"]
es = Elasticsearch([esHost])


def createAuditIndex():
    """
    数据铁笼的审计信息，每个铁笼的各个阶段的详细情况，加载参数情况,在区块链上，查询时，同一个铁笼的按照created_time_ms排序
    :return:
    """
    res = es.indices.exists(index="fcs_audit")
    print("fcs_audit es.indices.exists is ", res)
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
        res = es.indices.create(index='fcs_audit', body=mappings)
        print(res)


def recordAudit(operations, detail, record_id=None):
    """
    记录启动铁笼日志
    """
    if record_id is None:
        record_id = worker.get_id()
        print("id is", record_id)
    print("operation is ", operations)
    if operations == "":
        print("operations is none, return")
        return

    res = es.indices.exists(index="fcs_audit")
    if not res:
        # 创建索引,建立mapping索引
        print("请先创建索引fcs_audit")
    else:
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
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        createTime = now.strftime("%Y-%m-%d %H:%M:%S")
        # 更新数据
        action = {
            "id": record_id,
            "service_id": service_id,
            "service_name": serverName,
            "ops": operations,
            "block_id": "736473430",
            "block_number": 255323,
            "data_size": 1236,
            "detail": detail,
            "created_time": createTime,
            "created_time_ms": 1,
            "status": "成功"
        }
        print("record is ", action)
        res = es.index(index="fcs_audit", doc_type="doc", body=action)
        print("record result is ", res)


if __name__ == '__main__':
    environ = {
        "QUERY_STRING": "test=a"
    }
    createAuditIndex()
    # id = worker.get_id()
    # print(id)
