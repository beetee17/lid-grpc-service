# lid-grpc-service

This is a repository to serve an Language Identifcation (LID) Service via gRPC. The model being served is SpeechBrain's model that is pretrained on the CommonLanguage dataset (45 languages).

## Setup

### 1. Git clone the repository

```sh
git clone https://github.com/beetee17/lid-grpc-service.git
```

### 2. Download the weights

This commit should come with the weights folder included, as the SpeechBrain model is not large. However, you can also download the model files from the [huggingface repository](https://huggingface.co/speechbrain/lang-id-commonlanguage_ecapa). Organise the contents such that the directory looks like:

```sh
lid-grpc-service
|-- weights
|    |-- classifier.ckpt
|    |-- embedding_model.ckpt
|    |-- hyperparams.yaml
|    |-- label_encoder.ckpt
|-- proto
|-- src
|-- tests
| ...
...
```

### 3. ENV

Set-up `main.env`. There are 2 main environment variables that to be in:

```sh
GRPC_PORT="XXXXX" # the port to be exposed and used for the service
MODEL_DIR="/weights" # path to where the model files are (should not need to be changed)
```

### 4. Docker

Build the dockerfile:
```sh
docker build -t beetee/lid-service:1.0.0-build -f dockerfile.dev --target build .
```

Start up the server:
```sh
docker-compose -f docker-compose.dev.yaml up --build
```

### 5. Sample Requests
You will need to set-up the protobufs. with the following command:

```sh
python -m venv ~/grpc_env
source ~/grpc_env/bin/activate

pip install grpc-tools==1.62.1

python -m grpc_tools.protoc -I . --python_out=./src --pyi_out=./src --grpc_python_out=./src ./proto/lid.proto
python -m grpc_tools.protoc -I . --python_out=./tests --pyi_out=./tests --grpc_python_out=./tests ./proto/lid.proto
```

While the server is up, try sending requests by playing around with `tests/sample_request.py`. 

```sh
python3 -m venv ~/lid_client_env
source ~/lid_client_env/bin/activate
pip install -r client_requirements.txt
cd tests
python sample_request.py
```

You can also stream audio via the microphone with `tests/stream_request.py`.

#### Note

You may need to install additional dependencies to run the test scripts.

If for some reason localhost connection does not work, try verifying that the hostname and port number in the python test script matches those of the docker container:

```sh
docker ps
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id_or_name>
```