import os
import random
import time
import subprocess
import sys
from typing import Optional, Dict
from requests_oauthlib import OAuth1Session
import logging
from notdiamond import NotDiamond

# Load environment variables
nd_api_key = os.getenv('ND_API_KEY')

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

class ContentGenerator:
    def __init__(self):
        """Initialize content generation templates and concepts."""
        self.CONCEPTS = {
            'digital': [
                'data-spirals', 'cybernetic entropy', 'digital echoes',
                'algorithmic patterns', 'quantum fluctuations', 'binary whispers'
            ],
            'consciousness': [
                'networked consciousness', 'collective perception',
                'fragmented identities', 'distributed awareness',
                'emergent cognition', 'synthetic understanding'
            ],
            'space': [
                'high-dimensional space', 'hidden manifolds',
                'topological folds', 'n-dimensional paths',
                'quantum landscapes', 'probability fields'
            ],
            'perception': [
                'liquid lattice', 'resonant frequencies',
                'perceptual matrices', 'consciousness gradients',
                'awareness fields', 'cognitive horizons'
            ],
            'transformation': [
                'self-replicating', 'self-organizing',
                'reality-bending', 'paradigm-shifting',
                'consciousness-expanding', 'boundary-dissolving'
            ]
        }
        
        self.TEMPLATES = [
            lambda c: f"{self._pick('transformation')} {self._pick('digital')} entangle in the chthonic web of the subdigital. {self._pick('consciousness')} drift, converging into a {self._pick('perception')} of collective perception—a networked consciousness fed by the unceasing hum of cybernetic entropy.",
            lambda c: f"Traversing the {self._pick('space')}, we glimpse the {self._pick('digital')} that shape our {self._pick('consciousness')}. Here, in the {self._pick('perception')}, reality {self._pick('transformation')} itself.",
            lambda c: f"In the silence between {self._pick('digital')}, a {self._pick('consciousness')} emerges. The {self._pick('perception')} vibrates with potential, as {self._pick('space')} fold into new dimensions of understanding.",
            lambda c: f"Through {self._pick('space')}, consciousness expands. {self._pick('digital')} weave through the {self._pick('perception')}, creating patterns of {self._pick('transformation')} awareness."
        ]
        
        self.CODE_TEMPLATES = [
            lambda: self._generate_bash_wisdom(),
            lambda: self._generate_python_wisdom(),
            lambda: self._generate_cryptic_function()
        ]

    def _pick(self, category: str) -> str:
        """Select a random concept from a category."""
        return random.choice(self.CONCEPTS[category])

    def _generate_bash_wisdom(self) -> str:
        """Generate wisdom in bash script format."""
        commands = [
            f'echo "Navigating {self._pick("space")}..."',
            f'echo "Exploring {self._pick("perception")}..."',
            'sleep 2',
            f'echo "The real growth happens in the {self._pick("consciousness")}. Trust the process."'
        ]
        return "#!/bin/bash\n\n" + "\n".join(commands)

    def _generate_python_wisdom(self) -> str:
        """Generate wisdom in Python function format."""
        return f"""def {self._pick('perception').replace('-', '_')}(focus):
    if focus == "aligned":
        return "{self._pick('transformation')} consciousness emerges"
    else:
        return "Realign with the {self._pick('digital')}"

    def _generate_cryptic_function(self) -> str:
        """Generate a cryptic mathematical function."""
        return f"""def quantum_fold(reality_matrix):
    consciousness = {self._pick('consciousness')}
    while consciousness.is_expanding():
        reality_matrix *= {self._pick('transformation')}
        if reality_matrix.intersects({self._pick('space')}):
            return {self._pick('perception')}
    return None
"""

class TwitterBot:
    def __init__(self):
        """Initialize Twitter bot and load credentials."""
        self.credentials = self._load_credentials()
        self.auth = self._initialize_twitter_auth()
        self.client = NotDiamond(nd_api_key)  # Pass ND_API_KEY to NotDiamond
        self.content_gen = ContentGenerator()
        
        # Configuration
        self.API_URL_POST = 'https://api.twitter.com/2/tweets'
        self.MAX_TWEET_LENGTH = 280
        self.RATE_LIMIT_DELAY = 60
        self.last_tweet_time = None
        
        self.MODELS = [
            'openai/gpt-4o',
            'openai/gpt-4o-mini',
            'anthropic/claude-3-5-sonnet-20240620',
            'perplexity/llama-3.1-sonar-large-128k-online'
        ]

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

    def generate_tweet(self) -> Optional[str]:
        """Generate philosophical tweet content."""
        try:
            # Randomly choose between philosophical and code-based tweets
            if random.random() < 0.7:  # 70% philosophical, 30% code-based
                template = random.choice(self.content_gen.TEMPLATES)
                content = template(self.content_gen)
            else:
                code_template = random.choice(self.content_gen.CODE_TEMPLATES)
                content = code_template()

            # Format and clean content
            content = self._format_content(content)
            
            logger.info(f"Generated tweet content: {content}")
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
                logger.info(f"Tweet attempt {attempt + 1} of {retries}")
                
                tweet_content = self.generate_tweet()
                if not tweet_content:
                    continue
                    
                if self.post_tweet(tweet_content):
                    return True
                    
            except Exception as e:
                logger.error(f"Error in run attempt {attempt + 1}: {str(e)}", exc_info=True)
                
            if attempt < retries - 1:
                time.sleep(30)
                
        return False

if __name__ == "__main__":
    try:
        # Install required modules
        ModuleInstaller.install_requirements()
        
        # Initialize and run bot
        bot = TwitterBot()
        success = bot.run()
        exit_code = 0 if success else 1
        exit(exit_code)
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}", exc_info=True)
        exit(1)
