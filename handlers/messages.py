from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, Application
import google.generativeai as genai
import datetime
from config import Config
from textblob import TextBlob
import aiohttp
import asyncio
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


# MongoDB setup with MongoClient for synchronous calls
client = MongoClient(Config.MONGO_URI, server_api=ServerApi('1'))
db = client.get_database("telegram_bot")
users_collection = db.get_collection('users')
chat_history_collection = db.get_collection('chat_history')
file_metadata_collection = db.get_collection('file_metadata')
search_history_collection = db.get_collection('web_searches')

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update the path to where Tesseract is installed


async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "chat_id": update.message.chat_id,
        "phone_number": None
    }
    # Use MongoDB synchronous operation for this task
    users_collection.update_one(
        {"user_id": user.id},
        {"$setOnInsert": user_data},
        upsert=True
    )
    
    contact_keyboard = [[KeyboardButton("📱 Share Contact", request_contact=True)]]
    await update.message.reply_text(
        "Welcome! Please share your contact:",
        reply_markup=ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True)
    )


async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Help message...")

async def handle_contact(update: Update, context: CallbackContext):
    phone_number = update.message.contact.phone_number
    users_collection.update_one(
        {"user_id": update.message.from_user.id},
        {"$set": {"phone_number": phone_number}},
        upsert=True
    )
    await update.message.reply_text("Thank you for sharing your phone number!")

def get_message_content(message):
    if message.text:
        return message.text, "text"
    elif message.photo:
        return message.photo[-1].file_id, "photo"
    elif message.document:
        return message.document.file_id, "document"
    elif message.voice:
        return message.voice.file_id, "voice"
    elif message.audio:
        return message.audio.file_id, "audio"
    elif message.video:
        return message.video.file_id, "video"
    else:
        return None, "unknown"
    
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.05:
        return "positive"
    elif polarity < -0.05:
        return "negative"
    else:
        return "neutral"

def extract_text_from_image(image_path):

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"Error: {e}"

def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    full_text = ""
    
    for i, img in enumerate(images):
        img_path = f"temp_page_{i}.jpg"
        img.save(img_path, "JPEG")  # Save page as image
        full_text += extract_text_from_image(img_path) + "\n\n"
        os.remove(img_path)  # Remove temp image file

    return full_text.strip()

async def handle_message(update: Update, context: CallbackContext):
    message = update.effective_message
    user = update.effective_user

    content, content_type = get_message_content(message)

    
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)

    if content_type == "unknown":
        await message.reply_text("Sorry, I can't process this type of message yet.")
        return

    if content_type == "text":
        # Process text message
        sentiment = analyze_sentiment(content)
        response = await asyncio.to_thread(model.generate_content, content)
        
        chat_history = {
            "user_id": update.message.from_user.id,
            "query": content,
            "response": response.text,
            "sentiment": sentiment,
            "timestamp": datetime.datetime.now()
        }
        chat_history_collection.update_one(
            {"user_id": user.id},
            {"$setOnInsert": chat_history},
            upsert=True
        )
        
        # Add sentiment emoji
        emoji = "😁" if sentiment == 'positive' else "😄" if sentiment == 'neutral' else "🙂"
        full_response = f"{response.text} {emoji}"
        await update.message.reply_text(full_response)

    elif content_type == "photo":
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            
            if file:
                # Generate the filename based on the file_id
                filename = f"{file.file_id}.jpg"

                # Download the file to the specified path
                file_path = f"downloads/{filename}"
                await file.download_to_drive(file_path)
                
                # Extract text from the image (using your method or Google Vision API)
                extracted_text = extract_text_from_image(file_path)
                
                if not extracted_text:
                    extracted_text = "No text extracted from image."
                
                await update.message.reply_text(f"Generating response.... please wait.")
                
                # Proceed with further operations (description generation, metadata saving, etc.)
                model1 = genai.GenerativeModel('gemini-1.5-flash')
                response = await asyncio.to_thread(
                    model1.generate_content,
                    f"Based on the following extracted text, provide a description:\n\n{extracted_text}"
                )
                await update.message.reply_text(f"Response generated, analyzing .... please wait.")

                # Extract the description text from the response
                if response and response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts and len(candidate.content.parts) > 0:
                        description_text = candidate.content.parts[0].text
                    else:
                        description_text = "No description available."
                else:
                    description_text = "No description available."
                
                # Save metadata and respond to the user
                file_metadata = {
                    "user_id": update.message.from_user.id,
                    "filename": filename,
                    "description": description_text,
                    "timestamp": datetime.datetime.now()
                }
                
                file_metadata_collection.update_one(
                    {"user_id": update.message.from_user.id},
                    {"$setOnInsert": file_metadata},
                    upsert=True
                )
                
                await update.message.reply_text(f"File received! Description: {description_text}")
            else:
                await update.message.reply_text("Failed to retrieve the file.")
        else:
            await update.message.reply_text("No photo found in the message.")

    elif content_type == "document":
        file = await update.message.document.get_file()
        filename = update.message.document.file_name
        file_path = os.path.join(downloads_dir, filename)
        
        # Download the document file to the specified path
        await file.download_to_drive(file_path)
        
        if filename.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_path)  # Extract Text from PDF
        else:
            extracted_text = extract_text_from_image(file_path)  # Extract Text from Image

        if not extracted_text:
            extracted_text = "No text extracted from document."

        await update.message.reply_text(f"Generating response.... please wait.")
        
        # ----- Send the Extracted Text to the Generative Model -----
        model1 = genai.GenerativeModel('gemini-1.5-flash')
        response = await asyncio.to_thread(
            model1.generate_content,
            f"Based on the following extracted text, provide a description:\n\n{extracted_text}"
        )

        await update.message.reply_text(f"Response generated, analyzing .... please wait.")
        
        # Extract the description text from the response
        if response and response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts and len(candidate.content.parts) > 0:
                description_text = candidate.content.parts[0].text
            else:
                description_text = "No description available."
        else:
            description_text = "No description available."
        
        # Prepare the metadata for the file
        file_metadata = {
            "user_id": update.message.from_user.id,
            "filename": filename,
            "description": description_text,
            "timestamp": datetime.datetime.now()
        }
        
        file_metadata_collection.update_one(
            {"user_id": update.message.from_user.id},
            {"$setOnInsert": file_metadata},
            upsert=True
        )
        
        await update.message.reply_text(f"File received! Description: {description_text}")


async def handle_websearch(update: Update, context: CallbackContext):
    query = ' '.join(context.args)

    # Perform web search using Serper API
    search_results = await perform_web_search(query)
    update.message.reply_text(f"Searching...")

    summary_response = await asyncio.to_thread(model.generate_content, f"Summarize: {search_results}")
    summary = summary_response.text

    update.message.reply_text(f"Search complete, analyzing...")

    # Save search results to the database
    search_history = {
            "user_id": update.effective_chat.id,
            "query": query,
            "summary": summary,
            "links": [result.get('link') for result in search_results[:3]],
            "timestamp": datetime.datetime.now()
        }

    search_history_collection.update_one(
            {"user_id": update.effective_chat.id},
            {"$setOnInsert": search_history},
            upsert=True
        )
    
    await update.message.reply_text(f"🌐 Search Summary:\n{summary}")

async def perform_web_search(query):
    url = 'https://google.serper.dev/search'
    headers = {'X-API-KEY': Config.SERPER_API_KEY}
    params = {'q': query, 'gl': 'us', 'hl': 'en'}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('organic', [])  # Extract search results
            else:
                return []
