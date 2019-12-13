FROM kingproxj/python-serviceless:1.0.0

RUN mkdir -p /fcs

ADD . /fcs
WORKDIR /fcs

CMD ["/bin/sh", "-c", "python3 start.py"]
