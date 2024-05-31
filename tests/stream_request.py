""" test lid service """
# python3 -m grpc_tools.protoc -I . --python_out=./tests --pyi_out=./tests --grpc_python_out=./tests proto/asr.proto

import logging
import numpy as np
import soundfile as sf
import pyaudio
from tempfile import NamedTemporaryFile
import grpc

from proto import lid_pb2, lid_pb2_grpc

HOST = "localhost"
PORT = 40053

CHUNK_DURATION_MS = 5000
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

    with grpc.insecure_channel(f"{HOST}:{PORT}") as channel:
        stub = lid_pb2_grpc.LanguageIdentifierStub(channel)
        
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER
        )
        
        logging.info("Started Recording...")
        
        while True:
            audio_chunk = stream.read(FRAMES_PER_BUFFER)
            data = np.frombuffer(audio_chunk, np.float32)
            with NamedTemporaryFile(suffix=".wav") as f:
                sf.write(
                    file=f,
                    data=data,
                    samplerate=SAMPLE_RATE, 
                    format='WAV', 
                    subtype='PCM_16'
                )
                f.seek(0)
                audio_data = f.read()
            
                request = lid_pb2.LanguageIdentificationRequest(audio_data=audio_data)
                response = stub.identify_language(request)
                
                lang_code = response.language_code
                confidence = response.confidence

                logging.info("Detected language '%s' with probability %f" % (lang_code, confidence))
