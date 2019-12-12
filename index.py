# -*- coding: utf-8 -*-
from urllib import parse, request

def application(environ, start_response):
    entname = '山东惠硕信息技术有限公司'
    #result = calc_main_feature(entname)
    print(environ['QUERY_STRING'])
    result = "aaa"
    print(result)
    result = '<h1>Hello, %s!</h1>' % (environ['QUERY_STRING'][:] or 'web')
    responsebody = str(result)
    start_response('200 OK', [('Content-Type','application/json')])
    return [bytes(responsebody, encoding = "utf8")]