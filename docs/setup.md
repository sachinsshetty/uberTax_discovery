

git clone https://github.com/sachinsshetty/uberTax_discovery.git

cd uberTax_discovery

  - Build 
- docker compose -f lite-compose.yml build --no-cache

    - Run 
- docker compose -f lite-compose.yml up -d 


docker build --build-arg VITE_DWANI_API_BASE_URL=https://tax-server.dwani.ai -t dwani/ubertax-ui-prod -f prod.Dockerfile .