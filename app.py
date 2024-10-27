import os
import random
import time
import subprocess
import sys
from typing import Optional, Dict
from requests_oauthlib import OAuth1Session
import logging
from notdiamond import NotDiamond

# Load environment variables from repository secrets
nd_api_key = os.getenv("NOT_DIAMOND_API_KEY")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModuleInstaller:
    @staticmethod
    def install_requirements():
        """Install required Python modules."""
        required_modules = [
            'requests-oauthlib',
            'notdiamond',
            'requests'
        ]
        
        for module in required_modules:
            try:
                subprocess.check_call([
                    sys.executable, 
                    '-m', 
                    'pip', 
                    'install', 
                    '--upgrade',
                    module
                ])
                logger.info(f"Successfully installed {module}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {module}: {str(e)}")
                raise

class TwitterBot:
    def __init__(self):
        """Initialize Twitter bot and load credentials."""
        self.credentials = self._load_credentials()
        self.auth = self._initialize_twitter_auth()
        self.client = NotDiamond()  # Initialize NotDiamond client
        self.API_URL_POST = 'https://api.twitter.com/2/tweets'
        self.MAX_TWEET_LENGTH = 280
        self.RATE_LIMIT_DELAY = 60  # Time to wait between tweets
        self.last_tweet_time = None
        
    def _load_credentials(self) -> Dict[str, str]:
        """Load and validate Twitter API credentials from environment variables."""
        required_vars = [
            "ACCESS_TOKEN",
            "ACCESS_TOKEN_SECRET",
            "CONSUMER_KEY",
            "CONSUMER_SECRET"
        ]
        
        credentials = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            credentials[var] = value
        
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        return credentials

    def _initialize_twitter_auth(self) -> OAuth1Session:
        """Initialize Twitter OAuth session."""
        return OAuth1Session(
            client_key=self.credentials["CONSUMER_KEY"],
            client_secret=self.credentials["CONSUMER_SECRET"],
            resource_owner_key=self.credentials["ACCESS_TOKEN"],
            resource_owner_secret=self.credentials["ACCESS_TOKEN_SECRET"]
        )

    def generate_tweet(self) -> Optional[str]:
        """Generate tweet content using Not Diamond."""
        try:
            # Define the chat message to send to Not Diamond
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Concisely explain merge sort."}  # Adjust as needed
            ]
            
            # Call Not Diamond to get the best LLM response
            result, session_id, provider = self.client.chat.completions.create(
                messages=messages,
                model=[
                    'openai/gpt-4o',
                    'openai/gpt-4o-mini',
                    'anthropic/claude-3-5-sonnet-20240620'
                ]
            )

            content = result.content.strip()  # Get the response content
            logger.info(f"Generated tweet content: {content} using model: {provider.model}")

            # Format and clean content
            content = self._format_content(content)
            return content
            
        except Exception as e:
            logger.error(f"Error generating tweet content: {str(e)}", exc_info=True)
            return None

    def _format_content(self, content: str) -> str:
        """Format and clean tweet content."""
        content = ' '.join(content.split())
        
        if len(content) > self.MAX_TWEET_LENGTH - 6:
            content = content[:self.MAX_TWEET_LENGTH - 9] + "..."
            
        return content

    def post_tweet(self, content: str) -> bool:
        """Post tweet with error handling."""
        try:
            if self.last_tweet_time:
                elapsed = time.time() - self.last_tweet_time
                if elapsed < self.RATE_LIMIT_DELAY:
                    time.sleep(self.RATE_LIMIT_DELAY - elapsed)
            
            payload = {"text": content}
            response = self.auth.post(self.API_URL_POST, json=payload)
            response.raise_for_status()
            
            self.last_tweet_time = time.time()
            logger.info("Tweet posted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}", exc_info=True)
            return False

    def run(self, retries: int = 3) -> bool:
        """Main execution flow with retry logic."""
        for attempt in range(retries):
            try:
                logger.info(f"Tweet attempt {attempt + 1}/{retries}")
                content = self.generate_tweet()
                
                if content:
                    if self.post_tweet(content):
                        return True
                
                time.sleep(2)  # Short wait before retrying
            except Exception as e:
                logger.error(f"Unexpected error in run: {str(e)}", exc_info=True)
                time.sleep(2)  # Short wait before retrying
        
        logger.error("Failed to post tweet after multiple attempts")
        return False

if __name__ == "__main__":
    # Check if required modules are installed
    ModuleInstaller.install_requirements()

    bot = TwitterBot()
    bot.run()
