# ctranslate-deploy

This is a repository to serve an Language Identifcation (LID) Service via gRPC. The model being served is trained on ATC data. The model has been transformed, optimised and binarised with CTranslate2[https://github.com/OpenNMT/CTranslate2] for more efficient inference.

## Setup

### 1. Git clone the repository

```sh
git clone https://github.com/beetee17/lid-grpc-service.git
```

### 2. Download the weights

Please download the zip file containing the weights and other files with the link. (https://drive.google.com/file/d/12SSXquUX3hMeEWnUARaTQEHD7cD1DF4k/view?usp=drive_link). Unzip and place it in the `weights` folder. Directory should look like:

```sh
lid-grpc-service
|-- weights
|    |-- config.json
|    |-- model.bin
|    |-- tokenizer.json
|    |-- vocabulary.json
|-- proto
|-- src
|-- tests
| ...
...
```

### 3. ENV
Set-up the .env file (`main.env`) using the template at `.env_template`. There are 2 main environment variables that to be in:

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
python -m venv ~/lid_client_env
source ~/lid_client_env/bin/activate
pip install -r client_requirements.txt
cd tests
python sample_request.py
```

You can also stream audio via the microphone with `tests/stream_request.py`.

#### Note

You may need to install additional dependencies to run the test scripts.

Make sure to verify the hostname and port number in the python script match that of the docker container:

```sh
docker ps
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id_or_name>
```