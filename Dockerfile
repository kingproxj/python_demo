FROM kingproxj/python-serviceless:1.0.0

RUN mkdir -p /fcs \
    && pip install elasticsearch -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

ADD . /fcs
WORKDIR /fcs

CMD ["/bin/sh", "-c", "python3 download_models.py && sh replace.sh && python3 start.py"]
