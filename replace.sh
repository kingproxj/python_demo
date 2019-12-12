myhandler=$(echo $Handler | cut -d"." -f1)
myfunction=$(echo $Handler | cut -d"." -f2)
echo $myhandler $myfunction
handlerstr=$(echo 's/HandlerName/'$myhandler'/')
echo $handlerstr
sed -i $handlerstr server.py

functionstr=$(echo 's/FunctionName/'$myfunction'/')
echo $functionstr
sed -i $functionstr fcs_serverless_index.py
