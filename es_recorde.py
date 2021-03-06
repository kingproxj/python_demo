# -*- coding: utf-8 -*-
import os
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def record():
    """
    记录启动铁笼日志
    """
    esHost = os.environ["ES_SERVER_HOST"]
    es = Elasticsearch([esHost])

    res = es.indices.exists(index="fcs")
    if not res:
        # 创建索引,建立mapping索引
        mappings = {
            "mappings": {
                "type_doc": {  # type_doc_test为doc_type
                    "properties": {
                        "id": {
                            "type": "long",
                            "index": "false"
                        },
                        "name": {  # 服务名称
                            "type": "text",  # keyword不会进行分词,text会分词
                            "index": "true"  # 建索引
                        },
                        "namespace": {  # 命名空间
                            "type": "keyword",  # keyword不会进行分词,text会分词
                            "index": "true"  # 建索引
                        },
                        # functions可以存json格式，访问functions.content
                        "functions": {
                            "type": "object",
                            "properties": {
                                "handler": {"type": "keyword", "index": True},
                                "runtime": {"type": "keyword", "index": True},
                            }
                        },
                        "content": {
                            "type": "text",
                            "index": "false"
                        },
                        "createTime": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                        },
                        "updateTime": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                        }
                    }
                }
            }
        }
        print(mappings)
        res = es.indices.create(index='fcs', body=mappings)

    # 铁笼启动是否已经记录
    isRecorded = os.environ["IS_RECORD"]
    if isRecorded == "0":
        hostName = os.environ["HOSTNAME"]
        handler = os.environ["Handler"]
        runtime = os.environ["Runtime"]
        content = "启动铁笼" + hostName
        now = datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        createTime = now.strftime("%Y-%m-%d %H:%M:%S")

        # 插入数据
        action = {
            "id": "1111122222",
            "name": hostName,
            "namespace": "default",
            "functions": {"handler": handler, "runtime": runtime},
            "content": content,
            "createTime": createTime,
            "updateTime": createTime,
        }
        res = es.index(index="fcs", doc_type="type_doc", body=action)
        print(res)
        # {'_index': 'fcs', '_type': 'type_doc', '_id': 'z4dbDW8BtULaBa6qlsZO', '_version': 1, 'result': 'created', '_shards': {'total': 2, 'successful': 2, 'failed': 0}, '_seq_no': 0, '_primary_term': 1}
        if res.result == "created":
            os.environ["IS_RECORD"] = "1"


if __name__ == '__main__':
    record()
