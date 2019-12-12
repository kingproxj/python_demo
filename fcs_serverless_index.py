# -*- coding: utf-8 -*-
import HandlerName

def application(environ, start_response):
    entname = '山东惠硕信息技术有限公司'
    #result = calc_main_feature(entname)
    print("environ['QUERY_STRING']")
    result = HandlerName.FunctionName(environ, start_response)
    return result
