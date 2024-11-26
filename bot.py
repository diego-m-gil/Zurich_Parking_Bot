# bot.py

import logging
import json
import os
import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from geopy.distance import geodesic
from dotenv import load_dotenv
import re

# Load environment variables from .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the static data file
static_data_file = os.path.join(base_dir, 'data', 'parking_static_data.json')


def fetch_dynamic_data():
    url = 'http://www.pls-zh.ch/plsFeed/rss'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching dynamic data: {e}")
        return {}

    soup = BeautifulSoup(response.content, 'xml')

    dynamic_data = {}
    for item in soup.find_all('item'):
        title = item.find('title').text
        description = item.find('description').text
        name = title.split(' / ')[0]

        try:
            status, available_spots = description.split(' / ')
            available_spots = available_spots.strip()
            if available_spots.isdigit():
                available_spots = int(available_spots)
            else:
                available_spots = None
        except ValueError:
            status = description.strip()
            available_spots = None

        dynamic_data[name] = {
            'status': status,
            'available_spots': available_spots
        }
    return dynamic_data


async def start(update, context):
    await update.message.reply_text(
        "🚗 Welcome to *Zurich Parking Bot*! 🚗\n\n"
        "📍 Send me your location, and I'll find nearby parking spots for you. 🚘\n\n"
        "_Disclaimer: No personal information is stored._"
    )
    logger.info("Handled /start command.")


async def help_command(update, context):
    await update.message.reply_text(
        "❓ *How to use Zurich Parking Bot:*\n\n"
        "1️⃣ Share your location to find nearby parking spots.\n"
        "2️⃣ Receive details such as address, price, and distance.\n"
        "3️⃣ Click the provided link to navigate to the parking house.\n\n"
        "_Disclaimer: No personal information is stored._"
    )
    logger.info("Handled /help command.")


async def handle_location(update, context):
    user_location = (update.message.location.latitude, update.message.location.longitude)
    logger.info(f"Received location: {user_location}")

    # Load static data
    try:
        with open(static_data_file, 'r', encoding='utf-8') as f:
            static_data = json.load(f)
    except FileNotFoundError:
        logger.error("Static data file not found.")
        await update.message.reply_text("⚠️ Sorry, parking data is not available at the moment.")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        await update.message.reply_text("⚠️ There was an error processing parking data.")
        return

    # Fetch dynamic data
    dynamic_data = fetch_dynamic_data()
    if not dynamic_data:
        await update.message.reply_text("⚠️ Dynamic parking data is not available at the moment.")
        return

    radii = [1, 2, 3, 4, 5]  # in kilometers
    found_parkings = []
    for radius in radii:
        nearby_parkings = []
        for parking in static_data:
            name = parking.get('name')
            # Extract latitude and longitude from coordinates
            coords = parking.get('coordinates')
            if coords and len(coords) == 2:
                latitude = coords[0]
                longitude = coords[1]
                distance = geodesic(user_location, coords).meters  # Calculate distance
            else:
                latitude = None
                longitude = None
                distance = None

            # Extract dynamic data
            dynamic_info = dynamic_data.get(name, {})
            status = dynamic_info.get('status', 'N/A')
            available = dynamic_info.get('available_spots')

            # Add latitude, longitude, and distance to parking_info
            parking_info = {
                'name': name,
                'distance': int(distance) if distance is not None else "N/A",
                'available_spots': available,
                'status': status,
                'total_capacity': parking.get('total_capacity'),
                'link': parking.get('link'),
                'besonderes': parking.get('besonderes'),
                'normaltarif_1h': parking.get('normaltarif_1h'),
                'öffnungszeiten': parking.get('öffnungszeiten'),
                'latitude': latitude,
                'longitude': longitude,
                'address': parking.get('address'),
            }
            nearby_parkings.append(parking_info)
        if nearby_parkings:
            found_parkings = nearby_parkings
            logger.info(f"Found {len(found_parkings)} parkings within {radius} km radius.")
            break  # Stop searching further radii once parkings are found

    if found_parkings:
        # Filter out parkings with "N/A" distance
        valid_parkings = [p for p in found_parkings if isinstance(p['distance'], int)]

        # Sort valid parkings by distance
        valid_parkings.sort(key=lambda x: x['distance'])

        # Handle parkings with "N/A" distance separately if needed
        na_parkings = [p for p in found_parkings if not isinstance(p['distance'], int)]

        # Combine the lists if you want to include "N/A" distances at the end
        sorted_parkings = valid_parkings + na_parkings

        messages = []
        for parking in sorted_parkings[:5]:  # Limit to top 5 results
            name = parking['name']
            distance = parking['distance']
            available = parking['available_spots'] if parking['available_spots'] is not None else "N/A"
            total_capacity = parking['total_capacity'] if parking['total_capacity'] else "N/A"
            status = parking['status']
            occupancy = "N/A"
            if available != "N/A" and total_capacity != "N/A" and total_capacity != 0:
                try:
                    occupancy_value = (1 - available / total_capacity) * 100
                    occupancy = f"{occupancy_value:.2f}%"
                except ZeroDivisionError:
                    occupancy = "N/A"

            normaltarif = parking['normaltarif_1h'] if parking.get('normaltarif_1h') else "N/A"
            öffnungszeiten = parking['öffnungszeiten'] if parking.get('öffnungszeiten') else "N/A"
            latitude = parking.get('latitude')
            longitude = parking.get('longitude')
            # Create navigation link
            navigation_link = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}" if latitude and longitude else "Navigation not available"

            # Format the address to include a comma between street and zip code
            address = parking['address'] if parking.get('address') else "N/A"
            formatted_address = re.sub(r'(\D)(\d{4})', r'\1, \2', address)

            message = (
                f"🅿️ *{name}*\n"
                f"📍 *Address:* {formatted_address}\n"
                f"[➡️ Navigate Here](https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}\n)"
                f"📌 *Status:* {status}\n"
                f"📏 *Distance:* {distance} meters\n"
                f"🚘 *Available Spots:* {available} / {total_capacity}\n"
                f"📊 *Occupancy:* {occupancy}\n"
                f"💰 *Normaltarif (1h):* CHF {normaltarif}\n"
                f"⏰ *Öffnungszeiten:* {öffnungszeiten}\n"
                f"[ℹ️ More Info]({parking['link']})"
            )

            messages.append(message)
        response = f"✅ *Found parking spots within {radius} km radius:*\n\n" + "\n\n".join(messages)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        logger.info(f"Sent parking information to user within {radius} km radius.")
    else:
        await update.message.reply_text(
            "❌ No parking spots found within 5 km radius.\n"
            "🔄 Please send your location again to try a larger radius."
        )
        logger.info("No parking spots found within 5 km radius. Prompted user to resend location with a larger radius.")
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    logger.info("Bot started. Waiting for messages...")
    application.run_polling()


if __name__ == '__main__':
    main()
