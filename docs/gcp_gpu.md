Setup - L4 GPU on GCP 


If OPs Agents -Is running 

sudo systemctl stop google-cloud-ops-agent
sudo apt update && sudo apt install -y pciutils

curl -L https://storage.googleapis.com/compute-gpu-installation-us/installer/latest/cuda_installer.pyz --output cuda_installer.pyz

sudo python3 cuda_installer.pyz install_driver 

sudo python3 cuda_installer.pyz install_cuda 


https://cloud.google.com/compute/docs/gpus/install-drivers-gpu

--
Choose - Deep Learning - VM Images - with cuda 12.4 


--

add - daemon.json to /etc/docker

https://github.com/dwani-ai/docs/blob/main/files/daemon.json



sudo systemctl restart docker

