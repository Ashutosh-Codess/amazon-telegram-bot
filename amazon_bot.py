import sys
import os
import logging
import asyncio

from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# add SDK path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from creatorsapi_python_sdk.api_client import ApiClient
from creatorsapi_python_sdk.api.default_api import DefaultApi
from creatorsapi_python_sdk.models.search_items_request_content import SearchItemsRequestContent


# ---------- ENVIRONMENT VARIABLES ----------

BOT_TOKEN = os.getenv("BOT_TOKEN")
AMAZON_CLIENT_ID = os.getenv("AMAZON_CLIENT_ID")
AMAZON_CLIENT_SECRET = os.getenv("AMAZON_CLIENT_SECRET")

PARTNER_TAG = "misterrupee-21"
MARKETPLACE = "www.amazon.in"


# ---------- LOGGING ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# ---------- AMAZON SEARCH FUNCTION ----------
def search_amazon(keyword):

    api_client = ApiClient(
        credential_id=AMAZON_CLIENT_ID,
        credential_secret=AMAZON_CLIENT_SECRET,
        version="3.3"
    )

    api = DefaultApi(api_client)

    request = SearchItemsRequestContent(
        partner_tag=PARTNER_TAG,
        keywords=keyword,
        search_index="All",
        item_count=5
    )

    response = api.search_items(
        x_marketplace=MARKETPLACE,
        search_items_request_content=request
    )

    results = []

    if not response.search_result.items:
        return ["❌ No products found."]

    for item in response.search_result.items:

        title = item.item_info.title.display_value
        asin = item.asin

        link = f"https://www.amazon.in/dp/{asin}?tag={PARTNER_TAG}"

        message = f"""
🛒 Amazon Product

📦 {title}

🔗 {link}
"""

        results.append(message)

    return results


# ---------- TELEGRAM HANDLER ----------
async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):

    if update.message is None or update.message.text is None:
        return

    keyword = update.message.text.strip()

    await update.message.reply_text(f"🔍 Searching Amazon for: {keyword}")

    try:
        results = search_amazon(keyword)

        for product in results:
            await update.message.reply_text(product)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ---------- MAIN ----------
async def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot running...")

    await app.run_polling()


# ---------- RUN ----------
if __name__ == "__main__":
    asyncio.run(main())