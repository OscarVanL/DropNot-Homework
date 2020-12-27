FROM python:3

ADD . /dropnot
WORKDIR /dropnot

RUN pip install -r requirements.txt
CMD python -u ./main.py --server "$(pwd)/sync"
