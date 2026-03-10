import os
import asyncio
import aiohttp
from aiohttp import web
from pyrogram import Client, filters, idle

# Render Environment Variables se aayega data
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Teri Bun API ka URL (Environment variable me set karna)
TERA_API_URL = os.environ.get("TERA_API_URL", "http://localhost:5000/api")

app = Client("terabox_pro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def progress(current, total, msg):
    try:
        percent = round(current * 100 / total)
        if percent % 10 == 0:
            await msg.edit_text(f"🚀 **Uploading to Telegram... {percent}%**")
    except Exception:
        pass

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    text = (
        "Hello! 👋\n\n"
        "I am an advanced TeraBox Downloader Bot.\n"
        "Just send me any valid TeraBox link, and I will provide you with the direct file right here."
    )
    await message.reply_text(text)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_link(client, message):
    url = message.text
    
    if "terabox" not in url.lower():
        await message.reply_text("⚠️ **Invalid Link!** Please send a valid TeraBox URL.")
        return

    msg = await message.reply_text("⏳ **Processing your link, please wait...**")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TERA_API_URL}?url={url}") as response:
                if response.status != 200:
                    await msg.edit_text("❌ **API connection failed.** Please try again later.")
                    return
                
                data = await response.json()
                
                if data.get("status") != "success":
                    await msg.edit_text("❌ **Failed to fetch data.** The link might be private or invalid.")
                    return
                
                direct_link = data.get("download")
                filename = data.get("filename", "downloaded_video.mp4")
                file_size = data.get("size", "Unknown")
                
                await msg.edit_text(
                    f"✅ **Link Generated!**\n\n"
                    f"📁 **Name:** `{filename}`\n"
                    f"📊 **Size:** `{file_size}`\n\n"
                    f"⬇️ **Downloading file to server...**"
                )

                # Downloading file locally in chunks
                async with session.get(direct_link) as file_req:
                    with open(filename, 'wb') as f:
                        async for chunk in file_req.content.iter_chunked(1024 * 1024):
                            f.write(chunk)
                
                await msg.edit_text("✅ **Download complete! Uploading to Telegram 🚀**")

                # Uploading to Telegram
                await client.send_document(
                    chat_id=message.chat.id,
                    document=filename,
                    caption=f"🔥 **{filename}**\n\n~ @{client.me.username}",
                    progress=progress,
                    progress_args=(msg,)
                )
                
                os.remove(filename)
                await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ **An error occurred:** `{e}`")

# Render ke port check ke liye Dummy Web Server
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is running smoothly!")
    
    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Dummy Web Server Started on Port {port}")

async def main():
    await web_server() # Pehle web server start hoga Render ke liye
    await app.start()  # Fir tera Pyrogram bot start hoga
    print("Telegram Bot Started!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
