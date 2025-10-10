## UberTax 

- Website - [https://tax.dwani.ai](https://tax.dwani.ai)

Tax Technology Hackathon  - 2025

Pitch Deck - https://docs.google.com/presentation/d/1B0Yzv0tG1B0KZf5wnjUIklYcSSudUYmucbJDQocVtdM/edit?usp=sharing


--

docker build -t dwani/ubertax_ux:latest -f client.Dockerfile .
docker push dwani/ubertax_ux:latest

docker run -p 80:8000  dwani/ubertax_ux:latest

Server


docker build -t dwani/ubertax_server:latest -f server.Dockerfile .
docker push dwani/ubertax_server:latest

docker run -p 18888:18888 --env DWANI_API_BASE_URL=$DWANI_API_BASE_URL dwani/ubertax_server:latest
