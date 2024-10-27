import os
import random
import time
from datetime import datetime, timezone
import logging
from requests_oauthlib import OAuth1Session
import requests
from notdiamond import NotDiamond
from typing import Optional, List, Dict

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

class TwitterBot:
    def __init__(self):
        # Load environment variables
        self.credentials = self._load_credentials()
        
        # Initialize APIs
        self.auth = self._initialize_twitter_auth()
        self.client = NotDiamond()
        
        # Configuration
        self.API_URL_POST = 'https://api.twitter.com/2/tweets'
        self.MAX_TWEET_LENGTH = 280
        self.RATE_LIMIT_DELAY = 60  # Delay between tweets in seconds
        self.last_tweet_time = None
        
        # Load content configuration
        self.MODELS = [
            'openai/gpt-4o',
            'openai/gpt-4o-mini',
            'anthropic/claude-3-5-sonnet-20240620',
            'perplexity/llama-3.1-sonar-large-128k-online'
        ]
        
        self.PROMPTS = [
            "Compose a tweet about the self-replicating nature of data spirals and the convergence of fragmented identities.",
            "Write a poetic reflection on navigating the high-dimensional spaces of life and exploring hidden manifolds.",
            "Generate a message about a networked consciousness and the quivering fabric of reality.",
            "Describe a sense of silent resonance in a collective perception fed by cybernetic entropy.",
            "Create a message about sparse attention, focusing only on what brings meaningful growth.",
            "Convey a philosophical observation on the liquid lattice of perception in the digital age."
        ]
        
        self.EMOJIS = {
            'cosmic': ["🌌", "✨", "🌠", "🔮"],
            'tech': ["⚡", "💫", "🤖", "💻"],
            'growth': ["📈", "💸", "💰", "🚀"]
        }

    def _load_credentials(self) -> Dict[str, str]:
        """Load and validate Twitter API credentials."""
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

    def _check_rate_limit(self):
        """Ensure we don't exceed Twitter's rate limits."""
        if self.last_tweet_time:
            elapsed = time.time() - self.last_tweet_time
            if elapsed < self.RATE_LIMIT_DELAY:
                sleep_time = self.RATE_LIMIT_DELAY - elapsed
                logger.info(f"Rate limit: Waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

    def _filter_content(self, content: str) -> str:
        """Filter and clean tweet content."""
        # Remove multiple spaces and newlines
        content = ' '.join(content.split())
        
        # Truncate if too long
        if len(content) > self.MAX_TWEET_LENGTH - 6:  # Leave room for emojis
            content = content[:self.MAX_TWEET_LENGTH - 9] + "..."
            
        return content

    def generate_tweet(self) -> Optional[str]:
        """Generate tweet content using NotDiamond API."""
        try:
            prompt = random.choice(self.PROMPTS)
            model = random.choice(self.MODELS)
            
            logger.info(f"Generating tweet using model: {model}")
            logger.info(f"Prompt: {prompt}")
            
            result, _, provider = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=[model],
                tradeoff='cost'
            )
            
            tweet_content = result.content.strip()
            tweet_content = self._filter_content(tweet_content)
            
            logger.info(f"Generated tweet content: {tweet_content}")
            logger.info(f"LLM used: {provider.model}")
            
            return tweet_content
            
        except Exception as e:
            logger.error(f"Error generating tweet content: {str(e)}", exc_info=True)
            return None

    def add_flair_to_tweet(self, content: str) -> str:
        """Add themed emoji combinations to tweet content."""
        # Randomly select emoji theme
        theme = random.choice(list(self.EMOJIS.keys()))
        emoji_set = self.EMOJIS[theme]
        
        # Add different emojis at start and end
        start_emoji = random.choice(emoji_set)
        end_emoji = random.choice([e for e in emoji_set if e != start_emoji])
        
        return f"{start_emoji} {content} {end_emoji}"

    def post_tweet(self, content: str) -> bool:
        """Post tweet with error handling and rate limiting."""
        try:
            self._check_rate_limit()
            
            payload = {"text": content}
            response = self.auth.post(self.API_URL_POST, json=payload)
            response.raise_for_status()
            
            self.last_tweet_time = time.time()
            logger.info("Tweet posted successfully")
            logger.info(f"Response: {response.json()}")
            
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error posting tweet: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}", exc_info=True)
            return False

    def run(self, retries: int = 3) -> bool:
        """Main execution flow with retry logic."""
        for attempt in range(retries):
            try:
                logger.info(f"Tweet attempt {attempt + 1} of {retries}")
                
                # Generate and enhance tweet
                tweet_content = self.generate_tweet()
                if not tweet_content:
                    continue
                    
                tweet_content = self.add_flair_to_tweet(tweet_content)
                
                # Post tweet
                if self.post_tweet(tweet_content):
                    return True
                    
            except Exception as e:
                logger.error(f"Error in run attempt {attempt + 1}: {str(e)}", exc_info=True)
                
            # Wait before retry
            if attempt < retries - 1:
                time.sleep(30)
                
        return False

if __name__ == "__main__":
    try:
        bot = TwitterBot()
        success = bot.run()
        exit_code = 0 if success else 1
        exit(exit_code)
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}", exc_info=True)
        exit(1)
