from flask import Flask, redirect, url_for, request, session
from requests_oauthlib import OAuth1Session

app = Flask(__name__)
app.secret_key = '42ONMdu8fVecRgtv6WwZo-70K8frkHOBW4WJbF9JkcJI3BP82q'  # Replace with a real secret key for session management

# Your OAuth credentials
CONSUMER_KEY = 'yLKdAZZUnAJ8p0uufVWVNbp5f'
CONSUMER_SECRET = 'nGKWyUeJmjiTyw3GXDSLGXEbzt4Dvn2QBeYdkm8pWj5yy6ABnm'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
CALLBACK_URL = 'http://127.0.0.1:5000/callback'

@app.route('/')
def index():
    # Initiating the OAuth process
    twitter = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri=CALLBACK_URL)
    fetch_response = twitter.fetch_request_token(REQUEST_TOKEN_URL)
    session['request_token'] = fetch_response.get('oauth_token')
    session['request_token_secret'] = fetch_response.get('oauth_token_secret')
    authorization_url = twitter.authorization_url(AUTHORIZATION_URL)
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Getting the verifier and exchanging it for the access token
    request_token = session['request_token']
    request_token_secret = session['request_token_secret']
    oauth_verifier = request.args.get('oauth_verifier')

    twitter = OAuth1Session(CONSUMER_KEY,
                            client_secret=CONSUMER_SECRET,
                            resource_owner_key=request_token,
                            resource_owner_secret=request_token_secret,
                            verifier=oauth_verifier)

    access_token_response = twitter.fetch_access_token(ACCESS_TOKEN_URL)

    session['access_token'] = access_token_response.get('oauth_token')
    session['access_token_secret'] = access_token_response.get('oauth_token_secret')

    return f"Access Token: {session['access_token']}<br>Access Token Secret: {session['access_token_secret']}"

if __name__ == "__main__":
    app.run(debug=True)
