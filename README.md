# Project Name: Telegram bot

## Overview
This project implements a chatbot that integrates multiple advanced features such as image processing, document analysis, sentiment analysis, and AI-based text generation. The bot can handle user inputs, process images to extract text using OCR, analyze PDFs, and interact with generative AI models for intelligent responses. Additionally, the bot offers sentiment analysis with emoticons for user feedback and performs web searches based on user input.

## Features

### **1. Generative AI**:
The bot utilizes **Google Generative AI** for intelligent, context-aware responses. After processing the text from user inputs (whether extracted from images or PDFs), the bot sends the information to the Gemini model, which generates a response based on the input.

- **Library Used**: `google-generativeai`
- **How it works**: 
   - The bot processes incoming messages, including text, image and documents.
   - Once the text is extracted and processed, it is sent to **Google's Gemini model** to generate an appropriate response.
   - The bot then sends the response back to the user via Telegram.

### **2. MongoDB Integration**: 
The bot stores relevant user data, primarily the contact number, in **MongoDB**. This data can be used for future queries and interactions to provide a personalized experience. The collections gets updated within the specific user_id, the collections are namely, `users`,`chat_history`,`file_metadata` and `web_searches`.

- **Library Used**: `pymongo`
- **How it works**:
   - When users interact with the bot, their queries, extracted text from images or PDFs, and AI responses are stored in a MongoDB database.
   - This allows the bot to track previous interactions and use that data to improve user engagement.


### **3. OCR (Optical Character Recognition)**: 
The bot extracts text from images and scanned documents using **Tesseract OCR**. This allows users to upload images or screenshots containing text, and the bot will analyze and extract the text using the Tesseract library. The OCR feature is powered by the `pytesseract` library.

- **Library Used**: `pytesseract`
- **How it works**: 
   - When a user shares an image with the bot, the image is processed to extract the text from the image.
   - The extracted text is then sent to a **Google Gemini model** for further analysis and response generation.

### **3. PDF Text Extraction**: 
The bot can extract text from **PDF documents** using the `pdf2image` libraries. Users can share PDFs with the bot, and the bot will extract the textual content for further analysis.

- **Libraries Used**: `pdf2image`
- **How it works**:
   - When a user shares a PDF with the bot, it is processed using `pdf2image` to convert the PDF pages into images.
   - These images are then processed using OCR to extract the text using Tesseract OCR.
   - The extracted text is then analyzed and processed, similar to the image-to-text conversion process, with a response being generated via Google Generative AI.

### **4. Sentiment Analysis**: 
The bot performs sentiment analysis on the text it receives from users, such as in messages or extracted content from images and PDFs. It uses **TextBlob** to determine the sentiment of the content, and based on the sentiment, the bot will respond with emojis.

- **Sentiment Classification**:
   - If the sentiment is **positive**, a **happy emoji** (😁) is added to the response.
   - If the sentiment is **neutral**, a **satisfactory emoji** (😄) is used.
   - If the sentiment is **negative**, a **sad emoji** (🙂) is added to the response.
   
- **Library Used**: `textblob`
- **How it works**:
   - Sentiment analysis is done using `TextBlob.sentiment()`, which categorizes the text into positive, neutral, or negative sentiment.
   - Depending on the sentiment score, the bot replies with an appropriate emoji that reflects the mood.


### **6. Web Search**: 
The bot can perform **web searches** based on user input using the `aiohttp` library to send HTTP requests and get relevant search results.

- **Library Used**: `aiohttp`
- **How it works**:
   - Users can type `\websearch` followed by the search query to perform a web search.
   - The bot sends the query to a search engine API using `SERPER-API-KEY`.
   - The bot then processes the results and returns relevant information back to the user.

## How to Use the Bot

1. **Search for @HunlyBot** on Telegram or click [here](https://t.me/HunlyBot).
2. Type **`/start`** to begin the interaction.
3. **Share Contact**: You can share your contact with the bot to initiate further interactions.
4. **Text Prompts**: You can ask the bot for descriptions or any other content. For example:
   - Type a text prompt, and the bot will process it and perform sentiment analysis, responding with an emoji reflecting the sentiment.
5. **Share Images**: Share an image containing text, and the bot will extract text using Tesseract OCR, analyze it, and provide a response using the Google Generative AI model.
6. **Share PDFs**: Share a PDF document, and the bot will extract the text, analyze it, and provide a relevant response.
7. **Web Search**: Type `\websearch` followed by your query to perform a web search.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RaghavAror/telegram-bot.git
cd telegram-bot
```
2. Create a downloads/ folder in the directory.

3. Install all libraries.
```bash
pip install -r requirements.txt
```
4. Run the bot.
```bash
python main.py
```
5. To see the dashboard run following command.
```bash
python -m uvicorn analytics:app --reload 
```
