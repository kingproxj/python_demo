myhandler=$(echo $Handler | cut -d"." -f1)
myfunction=$(echo $Handler | cut -d"." -f2)
echo $myhandler $myfunction

handlerstr=$(echo 's/HandlerName/'$myhandler'/g')
echo $handlerstr
sed -i $handlerstr __fcs_serverless_index__.py

functionstr=$(echo 's/FunctionName/'$myfunction'/g')
echo $functionstr
sed -i $functionstr __fcs_serverless_index__.py
