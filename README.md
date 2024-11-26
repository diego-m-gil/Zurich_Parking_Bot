# Zurich Parking Bot

![Bot Banner](https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>/blob/main/banner.png?raw=true)

## Overview

**Zurich Parking Bot** is a Telegram bot designed to assist users in finding and managing parking spaces in Zurich. Leveraging automation tools like **Ansible** and **GitHub Actions**, the project demonstrates a robust CI/CD pipeline ensuring seamless deployments and updates.

## Features

- **Real-Time Parking Information:** Provides up-to-date information on available parking spaces.
- **User-Friendly Interface:** Easy interaction through Telegram commands.
- **Automated Deployment:** Utilizes Ansible for infrastructure automation.
- **Continuous Integration/Continuous Deployment:** Implemented via GitHub Actions for streamlined updates.

## Technologies Used

- **Programming Language:** Python 3
- **Telegram API:** For bot interactions
- **Ansible:** Automation tool for deployment
- **GitHub Actions:** CI/CD pipeline management
- **Ubuntu VPS:** Hosting the bot

## Project Structure

Zurich_Parking_Bot/ ├── ansible/ │ ├── inventory.ini │ ├── deploy_bot.yml │ └── deploy/ │ ├── bot.service │ └── .env ├── bot.py ├── requirements.txt ├── .gitignore └── README.md

markdown
Code kopieren

## Setup Instructions

### Prerequisites

- **Ubuntu VPS:** Ensure you have access to an Ubuntu server.
- **Git:** Installed on your local machine.
- **Ansible:** Installed in your WSL Ubuntu environment.
- **GitHub Repository:** [Zurich_Parking_Bot](https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>)

### 1. Clone the Repository

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
cd <YOUR_REPO_NAME>
2. Configure Ansible
Inventory File: Update ansible/inventory.ini with your VPS IP and SSH user.
ini
Code kopieren
[zurich_bot]
<YOUR_VPS_IP_ADDRESS> ansible_user=<YOUR_SSH_USERNAME>
Playbook: Ensure ansible/deploy_bot.yml has the correct repository URL and directories.
3. Deploy Using Ansible
bash
Code kopieren
ansible-playbook -i ansible/inventory.ini ansible/deploy_bot.yml
4. GitHub Actions for CI/CD
The repository includes a GitHub Actions workflow that automatically deploys updates to your VPS upon pushing changes to the main branch.

Workflow File: .github/workflows/deploy.yml
yaml
Code kopieren
name: Deploy Zurich Parking Bot

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Add Server to Known Hosts
        run: ssh-keyscan -H <YOUR_VPS_IP_ADDRESS> >> ~/.ssh/known_hosts

      - name: Run Ansible Playbook
        run: ansible-playbook -i ansible/inventory.ini ansible/deploy_bot.yml
Secrets Configuration:
SSH_PRIVATE_KEY: Add your private SSH key as a GitHub secret to enable the workflow to authenticate with your VPS.
Security Considerations
SSH Keys: Ensure your private keys are never exposed. Use GitHub Secrets to manage sensitive information.
Firewall: Configure UFW on your VPS to allow only necessary ports.
Regular Updates: Keep your server and dependencies up-to-date to mitigate vulnerabilities.
Demonstration


Interact with the Zurich Parking Bot on Telegram to see it in action.

Conclusion
The Zurich Parking Bot project not only provides a useful tool for managing parking in Zurich but also serves as a testament to effective deployment automation and CI/CD practices using Ansible and GitHub Actions. This setup ensures that updates are deployed reliably and efficiently, showcasing proficiency in modern DevOps methodologies.

Contact
For any inquiries or collaborations, feel free to reach out:

Email: your_email@example.com
LinkedIn: Your Name
markdown
Code kopieren

- **Placeholders:**
  - `<YOUR_GITHUB_USERNAME>`: Replace with your GitHub username.
  - `<YOUR_REPO_NAME>`: Replace with your GitHub repository name.
  - `<YOUR_VPS_IP_ADDRESS>`: Replace with your VPS's IP address.
  - `<YOUR_SSH_USERNAME>`: Replace with your SSH username (e.g., `ubuntu`).
  - `your_email@example.com`: Replace with your contact email.
  - `your-linkedin-profile`: Replace with your LinkedIn profile URL.

---

## **3. Additional Recommendations**

- **`.gitignore` Configuration:**

  Ensure your `.gitignore` includes paths to sensitive files to prevent them from being pushed to GitHub.

  ```gitignore
  # Byte-compiled / optimized / DLL files
  __pycache__/
  *.py[cod]
  *$py.class

  # C extensions
  *.so

  # Distribution / packaging
  .Python
  build/
  develop-eggs/
  dist/
  downloads/
  eggs/
  .eggs/
  lib/
  lib64/
  parts/
  sdist/
  var/
  *.egg-info/
  .installed.cfg
  *.egg

  # Virtual environments
  venv/
  .venv/
  ENV/
  env/
  env.bak/
  venv.bak/

  # PyCharm specific
  .idea/

  # Logs
  *.log

  # Secrets
  ansible/deploy/.env

  # Other
  *.sqlite3
