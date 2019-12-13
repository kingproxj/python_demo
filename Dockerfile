FROM kingproxj/python-serviceless:1.0.0
#
RUN yum install -y git && \
    git clone https://github.com/kingproxj/python_demo.git && \
    yum clean all && \
    cd python_demo && \
    python start.py
