""" lid Service """
import os
import io
import logging
import soundfile as sf
import numpy as np
import tempfile
from time import perf_counter
from concurrent import futures

# from faster_whisper import WhisperModel
from speechbrain.inference.classifiers import EncoderClassifier
from langcodes import SPEECHBRAIN_TO_WHISPER

import grpc
from proto import lid_pb2, lid_pb2_grpc

MODEL_DIR = os.environ["MODEL_DIR"]
DEVICE = "cuda"  # cuda or cpu
COMPUTE_TYPE = "float16"

class LanguageIdentifier(lid_pb2_grpc.LanguageIdentifierServicer):
    def __init__(self):
        self.model = EncoderClassifier.from_hparams(
            source=MODEL_DIR,
            savedir=MODEL_DIR
        )

    def identify_language(self, request, context):
        infer_start = perf_counter()

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                f.seek(0)
                f.write(request.audio_data)
                
                import shutil
                if os.path.exists(path="tmp"): shutil.rmtree("tmp")
                os.mkdir("tmp")
                
                signal = self.model.load_audio(f.name, savedir="tmp")
                probabilities, score, index, label =  self.model.classify_batch(signal)
                logging.info("Detected language '{}' with probability {}".format(
                        SPEECHBRAIN_TO_WHISPER.get(label[0], label[0]), score[0].item()
                    )
                )
                infer_end = perf_counter()
        
                logging.info("Inference elapsed time: %s", infer_end - infer_start)
                return lid_pb2.LanguageIdentificationResponse(
                    language_probabilities={ 
                            SPEECHBRAIN_TO_WHISPER.get(
                                self.model.hparams.label_encoder.decode_torch(np.array([i]))[0],
                                self.model.hparams.label_encoder.decode_torch(np.array([i]))[0]
                            ) : probabilities[0][i]
                            for i in range(len(probabilities[0]))
                    } 
                )
                
        except Exception as e:
            logging.error("There was an error detecting language in the audio. Error:", e)
            return lid_pb2.LanguageIdentificationResponse(language_code="???", confidence=0.0)
        
        
        
def serve():
    """Serves lid Model"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    lid_pb2_grpc.add_LanguageIdentifierServicer_to_server(LanguageIdentifier(), server)
    
    server.add_insecure_port(f"[::]:{os.environ['GRPC_PORT']}")
    server.start()

    logging.info("Server started, listening on port %s", os.environ["GRPC_PORT"])
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(message)s",
        level=logging.INFO
    )
    serve()
