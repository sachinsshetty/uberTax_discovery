## uberTax - Agentic Tax Analytics  

- juris-diction-AI-ry

#### powered by dwani.ai

--- 

- Top 3 Team 
    - Selected for Pitch at Tax Tech Conference, Frankfurt - November , 2025

- Live Demo - [https://tax.dwani.ai](https://tax.dwani.ai)

- Demo - [Video](https://youtu.be/FV0LxTmBZ5I)

- Pitch [deck](https://docs.google.com/presentation/d/e/2PACX-1vT0c8swMbrsw4MrN-b3AFY6Z3NtSea9AeTBPL-VuaDHjCA4r2obmFGWvcw-aSJ0DA/pub?start=false&loop=false&delayms=3000)

- Event
    - Tax Technology Hackathon  - 2025
        - October 10-12, 2025 
        - Frankfurt, Germany

- Team
    - Hueseyin
    - Sachin - [linkedIn](https://linkedin.com/in/sachinlabs)
    - Tobias

-- 

deployment

- server

    - docker compose -f deployment/server.yml up -d

- dashboard client
    - docker compose -f deployment/client.yml up -d
- dev client
    - docker compose -f deployment/dev-client.yml up -d 

- vllm
    - docker compose -f deployment/vllm.yml up -d 

<!--
--

curl -X POST "http://localhost:80/api/clients/natural-query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Show me all pending clients from USA"
  }'

docker build -t dwani/ubertax-dev -f client.Dockerfile .



PaddlePaddle/PaddleOCR-VL

HuggingFaceTB/SmolVLM-256M-Instruct

OpenGVLab/InternVL3_5-1B-Flash

OpenGVLab/InternVL3_5-1B-Instruct

OpenGVLab/InternVL3_5-2B-Instruct


With H100 GPU 
    - Build 
- docker compose -f lite-compose.yml build --no-cache

    - Run 
- docker compose -f lite-compose.yml up -d 

--
-->
