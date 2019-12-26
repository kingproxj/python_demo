myhandler=$(echo $Handler | cut -d"." -f1)
myfunction=$(echo $Handler | cut -d"." -f2)
echo $myhandler $myfunction
handlerFile=$myhandler'.py'
echo 'def '$myfunction'(environ, start_response):' > $handlerFile
echo '    result="test" ' >> $handlerFile
echo '    responsebody = str(result) ' >> $handlerFile
echo '    start_response("200 OK", [("Content-Type","application/json")]) ' >> $handlerFile
echo '    return [bytes(responsebody, encoding = "utf8")] ' >> $handlerFile
handlerstr=$(echo 's/HandlerName/'$myhandler'/g')
echo $handlerstr
sed -i $handlerstr __fcs_serverless_index__.py

functionstr=$(echo 's/FunctionName/'$myfunction'/g')
echo $functionstr
sed -i $functionstr __fcs_serverless_index__.py
