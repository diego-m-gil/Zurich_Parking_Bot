# ZhParkingBot

## Overview

ZhParkingBot is a Telegram bot designed to assist users in finding parking spaces in Zürich by providing real-time data from the [PLS Zürich RSS Feed](http://www.pls-zh.ch/plsFeed/rss). This data includes the current availability of parking spots in various parking houses, as well as their open/closed status.

You can start interacting with the bot directly by clicking here: [@ZhParkingBot on Telegram](https://t.me/ZhParkingBot).

The bot uses location-based services to help users find the nearest parking houses to their shared location. It calculates the distance between the user and the parking houses and provides detailed information, including:

- **Address**: The exact location of the parking house.
- **Price**: Information about parking costs.
- **Distance**: The distance from the user to each parking house.
- **Availability**: Current free spots in real-time.

Additionally, the bot includes direct navigation links for each parking house, making it easy to open the location in a navigation app and drive directly there.

### Example Interaction
<img src="https://i.imgur.com/6Jp4Dd9.png" alt="Example Interaction" width="400">



## Features

- **Real-Time Parking Updates:** Retrieves live parking availability data.
- **Location-Based Search:** Users can find nearby parking spaces by sharing their location.
- **Detailed Information:** Displays pricing, occupancy rates, distance, and operating hours.
- **Navigation Links:** Offers links to navigation apps for selected parking locations.
- **CI/CD Integration:** Automatically deploys updates with GitHub Actions.

## Technology Stack

- **Python:** Core bot logic and data processing.
- **Telegram Bot API:** User interaction and messaging.
- **Ansible:** Automates deployment on the server.
- **GitHub Actions:** Enables continuous integration and deployment.
- **BeautifulSoup & Requests:** Parses parking data from the PLS Zürich RSS feed.
- **Geopy:** Calculates distances for location-based parking recommendations.

## Project Structure

```
ZhParkingBot/
├── ansible/
│   ├── inventory.ini        # Ansible inventory file
│   ├── deploy_bot.yml       # Main playbook
│   └── deploy/
│       ├── bot.service      # Systemd service for the bot
│       └── .env             # Environment variables (excluded from Git)
├── bot.py                   # Main bot logic
├── data_fetcher.py          # Module for fetching and parsing parking data
├── requirements.txt         # Python dependencies
├── .gitignore               # Excludes sensitive files
└── README.md                # Documentation
```

## Setup

### Prerequisites

- A server (e.g., Ubuntu VPS) with Ansible installed.
- A GitHub repository with SSH access to your server.
- Python 3.8+ installed on the server.

### Deployment Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>
```

#### 2. Configure Ansible Inventory
Edit `ansible/inventory.ini` to include your server's IP and username:
```ini
[zh_parking_bot]
<YOUR_SERVER_IP> ansible_user=deployuser
```

#### 3. Deploy the Bot
Run the Ansible playbook:
```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy_bot.yml
```

#### 4. CI/CD with GitHub Actions
GitHub Actions workflow (`.github/workflows/deploy.yml`) automates deployment on every push to the `main` branch.

Update the workflow file to include your server details and add your SSH private key as a GitHub secret (`SSH_PRIVATE_KEY`).

## Usage

1. Open Telegram and start a conversation with the bot by clicking this link: [@ZhParkingBot](https://t.me/ZhParkingBot).
2. Send `/start` to begin interacting with the bot.
3. Share your location with the bot, and it will respond with nearby parking options, including:
   - Address
   - Price
   - Distance
   - Availability
4. Click on the provided navigation link to get directions to the parking spot.


## Security

- **SSH Keys:** Use GitHub Secrets to securely manage SSH private keys for CI/CD.
- **Environment Variables:** Store sensitive data like API keys in `.env` files, excluded from version control.
- **Server Hardening:** Use a firewall (e.g., UFW) and regularly update server packages.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or feedback, feel free to reach out.