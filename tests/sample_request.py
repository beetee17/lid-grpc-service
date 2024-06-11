""" test lid service """
# python3 -m grpc_tools.protoc -I . --python_out=./tests --pyi_out=./tests --grpc_python_out=./tests proto/lid.proto

import io
import time
import logging
import librosa
import soundfile as sf

import grpc

from proto import lid_pb2, lid_pb2_grpc

HOST = "localhost"
PORT = 40053

AUDIO_FILEPATH = "examples/short_chinese.wav"
SAMPLE_RATE = 16000
CHUNK_DURATION = 5

def stream_audio(
    stub: lid_pb2_grpc.LanguageIdentifierStub, 
    audio_file: str, 
    chunk_duration: float, 
    simulate: bool = False
):
    total_duration = librosa.get_duration(filename=audio_file)
    start_time = 0.0

    while start_time < total_duration:
        iteration_start_time = time.time()
        
        # end_time = min(start_time + chunk_duration, total_duration)
        # audio_data, sample_rate = librosa.load(
        #     audio_file, 
        #     sr=SAMPLE_RATE, 
        #     offset=start_time, 
        #     duration=end_time-start_time
        # )
        audio_data, sample_rate = librosa.load(
            audio_file, 
            sr=SAMPLE_RATE, 
            offset=start_time, 
            duration=CHUNK_DURATION
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

        logging.info("{} -> {}\n{}\n".format(
            start_time, start_time + CHUNK_DURATION, response.language_probabilities['zh']
            )
        )
            
        # start_time = end_time
        start_time += 0.5
        
        if simulate: time.sleep(max(0, (iteration_start_time + 1) - time.time()))
        
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