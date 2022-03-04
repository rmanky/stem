import os

import numpy as np
import torch

import boto3
from botocore.exceptions import ClientError

from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter

from scipy.io import wavfile
from io import BytesIO

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
device = torch.device('cpu')
seperator = Separator('spleeter:2stems')
audio_adapter = AudioAdapter.default()
rate = 44100

try:
  s3 = boto3.client('s3', aws_access_key_id=os.environ['VITE_AWS_ACCESS_STEM'], aws_secret_access_key=os.environ['VITE_AWS_SECRET_STEM'])
  print('Connected to S3')
except ClientError as e:
  print(e)

def handler(event, context):
    with open('/tmp/example.mp3', 'wb') as f:
        s3.download_fileobj(os.environ['VITE_AWS_BUCKET_STEM'], 'example.mp3', f)

    # spleeter
    waveform, _ = audio_adapter.load(os.join('/tmp/example.mp3'), sample_rate=rate)
    prediction = seperator.separate(waveform)

    print('Spleeter prediction created')

    bytes_wav = bytes()
    byte_io = BytesIO(bytes_wav)

    vocals = prediction['vocals']
    wavfile.write(byte_io, rate, vocals)
    data = byte_io.getvalue()

    s3.put_object(Bucket=os.environ['AWS_BUCKET_STEM'], Key='vocals.wav', Body=data, ContentType='audio/wav')

    print('Wrote vocals to S3')

    accompaniment = prediction['accompaniment']
    wavfile.write(byte_io, rate, accompaniment)
    data = byte_io.getvalue()

    s3.put_object(Bucket=os.environ['AWS_BUCKET_STEM'], Key='accompaniment.wav', Body=data, ContentType='audio/wav')

    print('Wrote accompaniment to S3')

    return response(f"Done!", 200)

def response(body, status_code, type='text/plain'):
    return {
        'statusCode': status_code,
        'body': body,
        'headers': {
            'Content-Type': type,
            'Access-Control-Allow-Origin': '*'
        }
    }