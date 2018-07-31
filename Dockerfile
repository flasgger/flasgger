FROM python:3.6

ADD . /flasgger
WORKDIR /flasgger

RUN pip3 install -U --no-cache-dir pip && \
    pip3 install --no-cache-dir -r requirements.txt -r requirements-dev.txt && \
    pip3 install --no-cache-dir etc/flasgger_package && \
    make test

EXPOSE 5000

CMD ["python3", "demo_app/app.py"]
