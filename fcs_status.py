# -*- coding: utf-8 -*-
import os
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from t_snowflake import IdWorker

worker = IdWorker(1, 2, 0)
esHost = os.environ["ES_SERVER_HOST"]
# esHost = "117.73.3.232:31103"
es = Elasticsearch([esHost])

def createStatusIndex():
    """
    记录启动铁笼日志，数据铁笼的运行监控信息，状态信息，由后台写入ES中，其文档id就是ids_id
    """
    res = es.indices.exists(index="fcs_status")
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
        print(mappings)
        res = es.indices.create(index='fcs_status', body=mappings)
        print("es.indices.create result is ", res)


def recordStatus():
    """
    记录启动铁笼日志，数据铁笼的运行监控信息，状态信息，由后台写入ES中，其文档id就是ids_id
    """
    # 铁笼启动是否已经记录
    isRecorded = os.environ["IS_RECORD"]
    hostName = os.environ["HOSTNAME"]
    handler = os.environ["Handler"]
    runtime = os.environ["Runtime"]
    serverName = os.environ["SERVER_NAME"]
    content = "启动铁笼" + hostName
    now = datetime.now()
    #print(now.strftime("%Y-%m-%d %H:%M:%S"))
    nowFormat = now.strftime("%Y-%m-%d %H:%M:%S")
    user_id = os.environ["creator"]
    if isRecorded == "0":
        id = worker.get_id()
        print("id is", id)
        # 插入数据
        action = {
            "id": id,
            "service_id": hostName,
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
        res = es.index(index="fcs_status", doc_type="doc", body=action)
        print("insert status result:", res)
        # {'_index': 'fcs', '_type': 'type_doc', '_id': 'z4dbDW8BtULaBa6qlsZO', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 2, 'failed': 0}, '_seq_no': 0, '_primary_term': 1}
        if res["result"] == "created":
            os.environ["IS_RECORD"] = res["_id"]
            print("IS_RECORD is ", os.environ["IS_RECORD"])
    else:
        # 更新数据
        action = {
            "doc": {
                # "id": isRecorded,
                # "service_id": hostName,
                # "service_name": serverName,
                # "request_id": "",
                # "user_id": user_id,
                # "company_name": "",
                # "live_time": 0,
                "destroy_time": nowFormat,
                # "created_time": createTime,
                "status": "已销毁",
                "blockchain": "数安链"
            }
        }
        print("update status", os.environ["IS_RECORD"])
        res = es.update(index="fcs_status", id=isRecorded, doc_type="doc", body=action)
        print("es.update result is", res)


if __name__ == '__main__':
    # environ = {
    #     "QUERY_STRING": "test=a"
    # }
    recordStatus()
    # id = worker.get_id()
    # print(id)
