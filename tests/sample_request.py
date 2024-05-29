""" test lid service """
# python3 -m grpc_tools.protoc -I . --python_out=./tests --pyi_out=./tests --grpc_python_out=./tests proto/lid.proto

import io
import time
import logging
import librosa
import numpy as np
import soundfile as sf

import grpc

from proto import lid_pb2, lid_pb2_grpc

HOST = "172.21.0.2"
PORT = 50052

AUDIO_FILEPATH = "examples/test_audio.wav"
SAMPLE_RATE = 16000
CHUNK_DURATION = 1.0

def stream_audio(
    stub: lid_pb2_grpc.LanguageIdentifierStub, 
    audio_file: str, 
    chunk_duration: float, 
    simulate: bool = True
):
    total_duration = librosa.get_duration(filename=audio_file)
    start_time = 0.0

    while start_time < total_duration:
        iteration_start_time = time.time()
        
        end_time = min(start_time + chunk_duration, total_duration)
        audio_data, sample_rate = librosa.load(
            audio_file, 
            sr=SAMPLE_RATE, 
            offset=start_time, 
            duration=end_time-start_time
        )

        with io.BytesIO() as temp_file:
            sf.write(
                file=temp_file, 
                data=audio_data,
                samplerate=sample_rate, 
                format='WAV', 
                subtype='PCM_16'
            )
            temp_file.seek(0)
            audio_data = temp_file.read()

        request = lid_pb2.LanguageIdentificationRequest(audio_data=audio_data)
        response = stub.identify_language(request)

        lang_code = response.language_code
        confidence = response.confidence

        logging.info("Detected language '%s' with probability %f" % (lang_code, confidence))
            
        start_time = end_time
        
        if simulate: time.sleep(max(0, (iteration_start_time + chunk_duration) - time.time()))
        
if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(message)s",
        level=logging.INFO
    )

    with grpc.insecure_channel(f"{HOST}:{PORT}") as channel:
        stub = lid_pb2_grpc.LanguageIdentifierStub(channel)
        stream_audio(
            stub, 
            audio_file=AUDIO_FILEPATH, 
            chunk_duration=CHUNK_DURATION
        )