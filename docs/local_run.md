Server - 
export VLLM_IP="0.0.0.0"
uvicorn server.main:app --host 0.0.0.0 --port 18889


Client - 
export DWANI_API_BASE_URL="0.0.0.0"
python ux/ux.py