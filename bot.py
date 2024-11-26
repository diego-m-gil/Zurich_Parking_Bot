# bot.py

import logging
import json
import os
import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from geopy.distance import geodesic
from config import TELEGRAM_TOKEN

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
        "Welcome to Zurich Parking Bot!\n"
        "Send me your location, and I'll find nearby parking spots."
    )
    logger.info("Handled /start command.")


async def help_command(update, context):
    await update.message.reply_text("Simply send your location to get started.")
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
        await update.message.reply_text("Sorry, parking data is not available.")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        await update.message.reply_text("Sorry, there was an error processing parking data.")
        return

    # Fetch dynamic data
    dynamic_data = fetch_dynamic_data()
    if not dynamic_data:
        await update.message.reply_text("Sorry, dynamic parking data is not available at the moment.")
        return

    radii = [1, 2, 3, 4, 5]  # in kilometers
    found_parkings = []
    for radius in radii:
        nearby_parkings = []
        for parking in static_data:
            name = parking.get('name')
            coords = parking.get('coordinates')
            if not name or not coords:
                continue  # Skip if essential data is missing

            dynamic_info = dynamic_data.get(name, {})
            status = dynamic_info.get('status', 'N/A')
            available = dynamic_info.get('available_spots')

            distance = geodesic(user_location, coords).meters
            if distance <= radius * 1000:  # Convert km to meters
                parking_info = {
                    'name': name,
                    'distance': int(distance),
                    'available_spots': available,
                    'status': status,
                    'total_capacity': parking.get('total_capacity'),
                    'link': parking.get('link'),
                    'besonderes': parking.get('besonderes'),
                    'normaltarif_1h': parking.get('normaltarif_1h'),
                    'öffnungszeiten': parking.get('öffnungszeiten')
                }
                nearby_parkings.append(parking_info)
        if nearby_parkings:
            found_parkings = nearby_parkings
            logger.info(f"Found {len(found_parkings)} parkings within {radius} km radius.")
            break  # Stop searching further radii once parkings are found

    if found_parkings:
        found_parkings.sort(key=lambda x: x['distance'])
        messages = []
        for parking in found_parkings[:5]:  # Limit to top 5 results
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

            message = (
                f"*{name}*\n"
                f"Status: {status}\n"
                f"Distance: {distance} meters\n"
                f"Available Spots: {available} / {total_capacity}\n"
                f"Occupancy: {occupancy}\n"
                f"Normaltarif (1h): CHF {normaltarif}\n"
                f"Öffnungszeiten: {öffnungszeiten}\n"
                f"[More Info]({parking['link']})"
            )
            messages.append(message)
        response = f"Found parking spots within {radius} km radius:\n\n" + "\n\n".join(messages)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        logger.info(f"Sent parking information to user within {radius} km radius.")
    else:
        # No parkings found within maximum radius
        await update.message.reply_text(
            "No parking spots found within 5 km radius.\n"
            "Would you like to try a larger radius? Please send your location again."
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
