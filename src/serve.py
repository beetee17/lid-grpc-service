""" lid Service """
import os
import logging
import datetime
import tempfile
from time import perf_counter
from concurrent import futures

from faster_whisper import WhisperModel

import grpc

from proto import lid_pb2, lid_pb2_grpc

MODEL_DIR = os.environ["MODEL_DIR"] + "/snapshots/model/"
DEVICE = "cuda"  # cuda or cpu
COMPUTE_TYPE = "float16"

class LanguageIdentifier(lid_pb2_grpc.LanguageIdentifierServicer):
    def __init__(self):
        self.model = WhisperModel(MODEL_DIR, device=DEVICE, compute_type=COMPUTE_TYPE)

    def identify_language(self, request, context):
        infer_start = perf_counter()

        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(request.audio_data)
            tmp.close()

            _, info = self.model.transcribe(tmp.name, beam_size=5)
            
            infer_end = perf_counter()
            
            logging.info("Inference elapsed time: %s", infer_end - infer_start)
            
            return lid_pb2.LanguageIdentificationResponse(
                language_code=info.language, 
                confidence=info.language_probability
            )

        except Exception as err:
            logging.error("There was an error detecting language in the audio. Error: {err}")
            return lid_pb2.LanguageIdentificationResponse(language_code="???", confidence=0.0)

        finally:
            os.unlink(tmp.name)

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
