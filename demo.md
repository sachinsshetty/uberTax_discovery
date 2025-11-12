- AI Tinkerers
- Document Parsing with Open Weight models 


    - Model - [Qwen3-VL-2B-instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct)

    - Inference - [vllm-qwen.yml](deployment/vllm-qwen.yml)
        - tool_parser : hermes  / NousResearch

    - PDF to Image  + 
Image to JSON
 [pdf-process](dashboard/backend/services/pdf_processor.py)

    - Text To SQL  / natural_query function   : [tool Call](dashboard/backend/routers/clients.py)