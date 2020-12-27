FROM python:3

ADD . /dropnot
WORKDIR /dropnot

RUN mkdir -p /dropnot/sync

RUN pip install -r requirements.txt
CMD python -u ./main.py --server sync