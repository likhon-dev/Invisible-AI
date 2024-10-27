import os
from requests_oauthlib import OAuth1Session
import requests
import openai

# Access Twitter API credentials from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

# Access OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# API endpoints
API_URL_POST = 'https://api.twitter.com/2/tweets'

# Initialize OAuth session for Twitter
auth = OAuth1Session(
    client_key=CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)

# Function to generate tweet content using OpenAI API
def generate_tweet(prompt="Generate a short, engaging tweet about AI advancements"):
    try:
        response = openai.Completion.create(
            engine="text-davinci-edit-001",  # You can use other models like 'gpt-4' if available
            prompt=prompt,
            max_tokens=50,             # Adjust the length as needed
            temperature=0.7            # Controls creativity; higher values make responses more random
        )
        tweet_content = response.choices[0].text.strip()
        print(f"Generated tweet content: {tweet_content}")
        return tweet_content
    except Exception as e:
        print(f"Error generating tweet content: {e}")
        return None

# Function to post a tweet
def post_tweet(content):
    try:
        payload = {"text": content}
        response = auth.post(API_URL_POST, json=payload)
        response.raise_for_status()  # Raises an error for HTTP error responses
        print("Tweet posted successfully:", response.json())
    except Exception as e:
        print(f"Error posting tweet: {e}")

# Main function
if __name__ == "__main__":
    # Generate tweet content
    tweet_content = generate_tweet()
    
    if tweet_content:
        # Post tweet if content was successfully generated
        post_tweet(tweet_content)
