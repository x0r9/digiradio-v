FROM python:3.8
COPY src/requirements.txt /opt/digiradio-v/requirements.txt
RUN pip install -r /opt/digiradio-v/requirements.txt
COPY src/ /opt/digiradio-v
WORKDIR /opt/digiradio-v
CMD uvicorn fast-demo:app --port 8080 --host 0.0.0.0

