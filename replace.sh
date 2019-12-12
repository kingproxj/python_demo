myhandler=$(echo $Handler | cut -d"." -f1)
myfunction=$(echo $Handler | cut -d"." -f2)
echo $myhandler $myfunction
handlerstr=$(echo 's/HandlerName/'$myhandler'/g')
echo $handlerstr
sed -i $handlerstr fcs_serverless_index.py

functionstr=$(echo 's/FunctionName/'$myfunction'/g')
echo $functionstr
sed -i $functionstr fcs_serverless_index.py
