FROM kingproxj/serverless-python3.7:1.0.0

RUN mkdir -p /fcs \
    && pip install elasticsearch -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

ADD . /fcs
WORKDIR /fcs

CMD ["/bin/sh", "-c", "sh replace.sh && python3 start.py"]
