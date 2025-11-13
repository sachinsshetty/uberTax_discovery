- AI Tinkerers
- Document Parsing with Open Weight models 

- PDF→image→VLM OCR→structured JSON→text-to-SQL 


    - Model - [Qwen3-VL-2B-instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct)

    - Inference - [vllm-qwen.yml](deployment/vllm-qwen.yml)
        - tool_parser : hermes  / NousResearch

    - PDF to Image  + 
Image to JSON
 [pdf-process](dashboard/backend/services/pdf_processor.py)

    - Text To SQL  / natural_query function   : [tool Call](dashboard/backend/routers/clients.py)

- Talk Link : https://berlin.aitinkerers.org/talks/rsvp_5W86mvFdiH0 