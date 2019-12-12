# -*- coding: utf-8 -*-
import index

def application(environ, start_response):
    entname = '山东惠硕信息技术有限公司'
    #result = calc_main_feature(entname)
    print("environ['QUERY_STRING']")
    result = index.application(environ, start_response)
    return result