""" test LID service """
# python3 -m grpc_tools.protoc -I . --python_out=./tests --pyi_out=./tests --grpc_python_out=./tests proto/lid.proto

import logging
import numpy as np
import pyaudio
import torch
import torchaudio

from speechbrain.inference.classifiers import EncoderClassifier

import grpc

from proto import vad_pb2, vad_pb2_grpc

HOST = "172.20.0.2"
PORT = 50052

CHUNK_DURATION_MS = 500
SAMPLE_RATE = 16000
FRAMES_PER_BUFFER=int(SAMPLE_RATE/1000 * CHUNK_DURATION_MS)

def int2float(sound):
    """
    Convert an array of integer audio samples to floating-point representation.

    Parameters:
    - sound (numpy.ndarray): Input array containing integer audio samples.

    Returns:
    - numpy.ndarray: Array of floating-point audio samples normalized to the range [-1, 1].
    """
    sound = sound.astype('float32')

    # Scale the floating-point values to the range [-1, 1] if the input audio is not silent
    if np.abs(sound).max() > 0: sound *= 1 / 32768

    # Remove single-dimensional entries from the shape of the array
    sound = sound.squeeze()

    return sound


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(message)s",
        level=logging.INFO
    )
    
    language_id = EncoderClassifier.from_hparams(
        source="speechbrain/lang-id-commonlanguage_ecapa", 
        savedir="model/"
    )

    language_id = EncoderClassifier.from_hparams(source="model/")
    
    # signal = language_id.load_audio("examples/test_audio_full.wav")
    # prediction =  language_id.classify_batch(signal)
    # print(prediction[3])

    with grpc.insecure_channel(f"{HOST}:{PORT}") as channel:
        stub = vad_pb2_grpc.VoiceActivityDetectorStub(channel)
        
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER
        )
        
        logging.info("Started Recording...")
        
        while True:
            audio_chunk = stream.read(FRAMES_PER_BUFFER)
            
            audio_int16 = np.frombuffer(audio_chunk, np.int16)

            audio_float32 = int2float(audio_int16)
            
            tensor = torch.from_numpy(audio_float32)
            
            prediction = language_id(tensor)
            
            # Predicted Language, Confidence
            print(prediction[3], prediction[1])
