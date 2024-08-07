from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import openai
import uvicorn
import asyncio
from twikit import Client
import nest_asyncio
from  twitter import tweeteeer
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import openai
import uvicorn

import re
import json
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    load_index_from_storage
)
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.core.node_parser import SentenceSplitter

import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import requests
from bs4 import BeautifulSoup
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
app = FastAPI()


AI71_BASE_URL = "https://api.ai71.ai/v1/"
AI71_API_KEY = "api71-api-80c0a825-4344-4ed1-be16-574f9d0a2f53"

client = openai.OpenAI(
    api_key=AI71_API_KEY,
    base_url=AI71_BASE_URL,
)

twitter_client = Client('en-IN')
USERNAME = 'nickalodean9'
EMAIL = 'nickalodean9@gmail.com'
PASSWORD = 'Nickalodean9'


async def login_to_twitter():
    await twitter_client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
    )

async def post_to_twitter(text):
    await twitter_client.create_tweet(
        text=text,
        media_ids=None
    )

@app.post("/generate")
async def generate(request: Request):
    user_query = (await request.body()).decode("utf-8")
    # data = await request.json()
    # user_query = data.get("user_query", "")

    AI71_BASE_URL = "https://api.ai71.ai/v1/"
    AI71_API_KEY = "api71-api-00f56960-f31c-46ef-bade-93bf8f54d4ad"
    #user_query=request
    chat = ChatOpenAI(
        model="tiiuae/falcon-180B-chat",
        api_key=AI71_API_KEY,
        base_url=AI71_BASE_URL,
        streaming=True,
    )

    print(
        chat.invoke(
            [
                SystemMessage(content="""You are a helpful assistant, """),
                HumanMessage(content="Hello!"),
            ]
        )
    )

    # Streaming invocation:
    s = user_query
    response = ""

    for chunk in chat.stream(f"""I am planning to launch a {s} service and need assistance in generating relevant questions based on user queries.
    Give me three questions regarding this product that can keep me updated as per user needs."""):
        response += chunk.content
        #print(chunk.content, end="", flush=True)

    json_match = re.search(r'\{.*?\}', response, re.DOTALL)

    # Use regex to extract separate question entries
    separate_match = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\nUser:|\Z)', response, re.DOTALL)

    extracted_questions = {}
    extracted_questions_list = []  # List to store all extracted questions

    if json_match:
        json_data = json_match.group(0).strip()  # Extract and strip the JSON string

        try:
            # Parse the JSON string into a Python dictionary
            questions = json.loads(json_data)

            # Extract only the questions
            for key, value in questions.items():
                extracted_questions[key] = value["question"]
                extracted_questions_list.append(value["question"])  # Add to the list

        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

    if separate_match:
        for index, question_text in enumerate(separate_match, start=1):
            question_id = f"Q{index}"
            extracted_questions[question_id] = question_text.strip()
            extracted_questions_list.append(question_text.strip())  # Add to the list

    # Print the extracted questions
    if extracted_questions:
        #print("Extracted Questions:")
        #print(json.dumps(extracted_questions, indent=4))  # Pretty-print the JSON

        # Save to a JSON file
        with open('questions.json', 'w') as json_file:
            json.dump(extracted_questions, json_file, indent=4)

    # Print the list of extracted questions
    #print("List of Extracted Questions:")
    #for question in extracted_questions_list:
        #print(f"- {question}")

    # List of search queries
    search_queries = extracted_questions_list#["skincare trends site: vogue", "skincare products remedies", "top skincare products alternatives"]
    #search_queries = ["Who took the most wickets in the 2nd ODI match between India and Sri Lanka on 4th August 2024?"]
    # Google search URL
    def google_search_url(query):
        return f"https://www.google.com/search?q={query}"

    # Function to perform search and extract links
    def fetch_links_from_search(query):
        search_url = google_search_url(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a['href'] for a in soup.select('div#search div.g a') if 'href' in a.attrs]
        return links[:5]

    # Function to scrape content from a given URL
    def scrape_content(url):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract the main content
            main_content = soup.get_text(separator='\n', strip=True)
            # Clean up the content
            main_content = re.sub(r'\s+', ' ', main_content)
            return main_content
        except requests.RequestException as e:
            #print(f"Error fetching {url}: {e}")
            return None
    # Initialize a variable to hold all content
    all_content = ""

    # Loop through each search query
    for j, search_query in enumerate(search_queries, start=1):
        #print(f"Processing query {j}: {search_query}")

        # Fetch links from Google search
        links = fetch_links_from_search(search_query)

        # Loop through the links
        for i, link in enumerate(links, start=1):
            #print(f"Scraping link {i}: {link}")

            # Scrape the content
            content = scrape_content(link)
            if content:
                # Append the content to the all_content variable
                all_content += content + "\n"  # Adding a newline for separation

    # Save all content to a single file
    with open("combined_search_results.txt", "w", encoding="utf-8") as file:
        file.write(all_content)

    #print("Scraping complete. All content saved to combined_search_results.txt.")
    x=all_content
    all_content=x[0:4000]

    chat = ChatOpenAI(
        model="tiiuae/falcon-180B-chat",
        api_key=AI71_API_KEY,
        base_url=AI71_BASE_URL,
        streaming=True,
    )

    # Simple invocation:
    print(
        chat.invoke(
            [
        #     {"role": "system", "content": """based on this provide me some better post that target {product_name} for product launch.
        # I want only post content with important #tags for posting on Twitter (as per text constraints for thread length).
        # Please don't include these type of text like 'Here's a potential Twitter post for launching your "{product_name}".'.
        # I want to post directly on Twitter and please generate the content only within 480 characters."""},
            {"role": "user", "content": f"""based on this provide me some better post that target for product launch.
        I want only post content with important #tags for posting on Twitter (as per text constraints for thread length).
        Please don't include these type of text like 'Here's a potential Twitter post with emogi for launching your .'.
        I want to post directly on Twitter and please generate the content only within 280 characters.\n{all_content}"""},
        ],
        )
    )


    # Streaming invocation
    s = user_query
    response_chunks = []

    # Using an f-string to insert the product name into the Twitter post
    for chunk in chat.stream(f"Write a post regarding the launch of {s} on Twitter with #{s.replace(' ', '')}:"):
        response_chunks.append(chunk.content)  # Store each chunk in the list
    # Join all the chunks into a single string
    full_response = ''.join(response_chunks)

    # Print the full response
    #print(full_response)
    return {"output": full_response.strip()}


@app.post("/post_to_twitter")
async def post_to_twitter_endpoint(request: Request):
    text = (await request.body()).decode("utf-8")
    print("twitter text___________:",text)
    await tweeteeer(text[:180])
    return {"message": "posted bhaiya"}

@app.get("/")
async def index():
    return FileResponse("index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.2", port=5000)
