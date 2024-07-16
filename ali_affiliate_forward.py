import re
import logging
from telethon import TelegramClient, events
from aliexpress_api import AliexpressApi, models
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration
KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
TRACKING_ID = os.getenv('TRACKING_ID')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
SOURCE_CHANNEL_ID = int(os.getenv('SOURCE_CHANNEL_ID'))
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))

# Initialize Aliexpress API client
aliexpress = AliexpressApi(KEY, SECRET, models.Language.EN, models.Currency.EUR, TRACKING_ID)

# Initialize Telegram client
client = TelegramClient('anon', API_ID, API_HASH)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_client():
    try:
        await client.start(PHONE_NUMBER)
        logger.info("Client started...")
    except Exception as e:
        logger.error(f"Error starting client: {e}")
        return


@client.on(events.NewMessage(chats=SOURCE_CHANNEL_ID))
async def message_handler(event):
    try:
        message_text = event.message.message
        original_link = find_link_in_message(message_text)

        if original_link:
            affiliate_link = generate_affiliate_link(original_link)
            if affiliate_link:
                event.message.message = message_text.replace(original_link, affiliate_link)
                await client.send_message(TARGET_CHANNEL_ID, event.message)
                logger.info(f"Message successfully sent with new link: {affiliate_link}")
            else:
                logger.warning("Failed to create affiliate link")
        else:
            logger.info("No link found in the message")
    except Exception as e:
        logger.error(f"Error processing message: {e}")


def find_link_in_message(message):
    match = re.search(r'https?://\S+', message)
    if match:
        original_link = match.group(0)
        logger.info(f"Found link: {original_link}")
        return original_link
    return None


def generate_affiliate_link(original_link):
    try:
        affiliate_links = aliexpress.get_affiliate_links(original_link)
        if affiliate_links:
            affiliate_link = affiliate_links[0].promotion_link
            logger.info(f"Affiliate link successfully created: {affiliate_link}")
            return affiliate_link
    except Exception as e:
        logger.error(f"Error creating affiliate link: {e}")
    return None


async def main():
    await start_client()
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Main process error: {e}")
