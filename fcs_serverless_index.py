# -*- coding: utf-8 -*-
import HandlerName

def application(environ, start_response):
    print("environ['QUERY_STRING']")
    result = HandlerName.FunctionName(environ, start_response)
    return result
