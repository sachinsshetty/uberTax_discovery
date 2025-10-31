Project Installation


- deployment

    - Dashboard 
        - server
            - docker compose -f deployment/server.yml up -d

        - dashboard client
            - docker compose -f deployment/client.yml up -d
        - dev client
            - docker compose -f deployment/dev-client.yml up -d 

        - vllm
            - docker compose -f deployment/vllm.yml up -d 

    - Analytics
        - docker compose -f analytics/compose.yml up -d



- docker 

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc


sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```bash

sudo docker run hello-world


sudo groupadd docker

sudo usermod -aG docker $USER

newgrp docker

docker run hello-world
```



---


- vLLM setup - Model serving

    ```bash
    sudo apt update

    sudo apt install python3.12 python3.12-venv python3.12-dev poppler-utils -y


    python3.12 -m venv venv
    source venv/bin/activate

    pip install torch==2.7.1 torchaudio==2.7.1 torchvision --index-url https://download.pytorch.org/whl/cu128


    pip install https://github.com/dwani-ai/vllm-arm64/releases/download/v.0.0.4/vllm-0.10.1.dev0+g6d8d0a24c.d20250726-cp312-cp312-linux_aarch64.whl

    ```

- Full - GPU 

    ```bash
    vllm serve RedHatAI/gemma-3-27b-it-FP8-dynamic --served-model-name gemma3 --host 0.0.0.0 --port 9000 --gpu-memory-utilization 0.9 --tensor-parallel-size 1 --max-model-len 98304 --disable-log-requests --dtype bfloat16 --enable-chunked-prefill --enable-prefix-caching --max-num-batched-tokens 8192 --chat-template-content-format openai
    ```

- Half GPU

    ```bash

    vllm serve RedHatAI/gemma-3-12b-it-FP8-dynamic --served-model-name gemma3 --host 0.0.0.0 --port 9000 --gpu-memory-utilization 0.5 --tensor-parallel-size 1 --max-model-len 32768 --disable-log-requests --dtype bfloat16 --enable-chunked-prefill --enable-prefix-caching --max-num-batched-tokens 8192 --chat-template-content-format openai
    ```

---


- Docker builds

- analytics
    - client
        ```bash
        cd analytics
        docker build -t dwani/ubertax_ux:latest -f client.Dockerfile .
        docker push dwani/ubertax_ux:latest

        docker run -p 80:8000  dwani/ubertax_ux:latest
        ```
    - Server

        ```bash
        docker build -t dwani/ubertax_server:latest -f server.Dockerfile .
        docker push dwani/ubertax_server:latest
        docker run -p 18888:18888 --env DWANI_API_BASE_URL=$DWANI_API_BASE_URL dwani/ubertax_server:latest
        ```

- Dashboard
    - Client
        ```bash
        cd dashboard/tax-ui 
        docker build -t dwani/ubertax-dev -f Dockerfile .
        docker push dwani/ubertax-dev
        ```
    - Server

        ```bash
        cd dashboard/backend
        docker build -t dwani/ubertax-server:latest -f Dockerfile .
        docker push dwani/ubertax-server
        ```