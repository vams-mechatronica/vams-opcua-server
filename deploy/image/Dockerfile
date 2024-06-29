FROM python:3.9-slim
WORKDIR /app/opcua/server
COPY src/requirements.txt /app/opcua/server/

RUN apt-get update && apt-get install -y \
build-essential \
libssl-dev \
libffi-dev \
python3-dev 

RUN pip3 install -r requirements.txt
EXPOSE 4840
CMD [ "python3", "server.py" ]