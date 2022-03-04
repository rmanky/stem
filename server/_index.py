import os
from os.path import join

# boto3
import boto3
from botocore.exceptions import ClientError

from http.server import BaseHTTPRequestHandler
from io import BytesIO
from scipy.io import wavfile

# spleeter
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
seperator = Separator('spleeter:2stems')
audio_adapter = AudioAdapter.default()
rate = 44100

try:
  s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_STEM'], aws_secret_access_key=os.environ['AWS_SECRET_STEM'])
  print('Connected to S3')
except ClientError as e:
  print(e)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('GET request received')
        # send response
        self.send_response(200)
        # regular text
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        # spleeter
        waveform, _ = audio_adapter.load(join('data','example.wav'), sample_rate=rate)
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

        # send buffer to client
        self.wfile.write('Done, waiting on S3...'.encode('utf-8'))
        return