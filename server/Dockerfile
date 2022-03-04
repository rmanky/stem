FROM python:3.7-slim

COPY app.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

WORKDIR /

COPY ffmpeg.tar.xz .
ADD ffmpeg.tar.xz /usr/bin

RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "app.handler" ]