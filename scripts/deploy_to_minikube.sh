#!/bin/bash
# =====================================================================
# Minikube & Ansible Deployment Script (Run inside WSL)
# Description: Installs Ansible in WSL, connects to Minikube, and runs the playbook.
# =====================================================================

echo -e "\e[36mStarting Kubernetes Deployment via Ansible...\e[0m"

# 1. Start Minikube if not running (assumes minikube is available in PATH via Windows interop or installed in WSL)
echo -e "\e[33mChecking Minikube status...\e[0m"
if ! minikube.exe status | grep -q "Running"; then
    echo -e "\e[32mStarting Minikube...\e[0m"
    minikube.exe start --driver=docker
else
    echo -e "\e[32mMinikube is already running.\e[0m"
fi

# 2. Install Ansible if not installed
if ! command -v ansible &> /dev/null; then
    echo -e "\e[33mAnsible not found. Installing Ansible...\e[0m"
    sudo apt-get update
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository --yes --update ppa:ansible/ansible
    sudo apt-get install -y ansible
else
    echo -e "\e[32mAnsible is already installed.\e[0m"
fi

# 3. Navigate to Ansible directory and run playbook
cd /mnt/c/Users/Ruturaj/Desktop/SPE_MP/ansible || { echo "Failed to find ansible directory!"; exit 1; }

echo -e "\e[33mRunning Ansible Playbook (site.yml)...\e[0m"
# Use localhost as connection local since we deploy to the current k8s context
ansible-playbook -i hosts.ini site.yml --connection=local

echo -e "\e[36m=====================================================================\e[0m"
echo -e "\e[32mDeployment script completed! Check Kubernetes resources with:\e[0m"
echo -e "\e[32mkubectl get pods -n spe-namespace\e[0m"
echo -e "\e[36m=====================================================================\e[0m"
