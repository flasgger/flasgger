FROM python:3.6

ADD . /flasgger
WORKDIR /flasgger

RUN pip install -U --no-cache-dir pip && \
    pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt && \
    pip install --no-cache-dir etc/flasgger_package && \
    make test && \
    python setup.py sdist bdist_wheel --universal

EXPOSE 5000

CMD ["python3", "demo_app/app.py"]
