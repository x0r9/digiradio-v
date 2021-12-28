FROM python:3.7
COPY src/requirements.txt /opt/digiradio-v/requirements.txt
RUN pip install -r /opt/digiradio-v/requirements.txt
COPY src/ /opt/digiradio-v
#RUN pip install /tmp/myapp
CMD uvicorn /opt/digiradio-v/fast-demo:app --port 8080

