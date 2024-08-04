import tweepy
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 50,
    "response_mime_type": "text/plain",
}

class TwitterBot:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
            wait_on_rate_limit=True
        )

    def check_mentions(self):
        try:
            # Get the bot's user ID
            user = self.client.get_me()
            user_id = user.data.id

            # Get recent mentions
            mentions = self.client.get_users_mentions(
                id=user_id,
                tweet_fields=["created_at", "text"]
            )
            return mentions.data if mentions.data else []
        except tweepy.TweepyException as e:
            print(f"Error fetching mentions: {e}")
            return []

    def respond_to_mention(self, tweet):
        try:
            # Extract original tweet content
            original_tweet_id = tweet.referenced_tweets[0].id
            original_tweet = self.client.get_tweet(original_tweet_id)
            original_text = original_tweet.data.text

            # Generate a response using Gemini AI
            chat_session = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
            ).start_chat(history=[])
            response = chat_session.send_message(f"reply to this tweet with topnotch humor, wit and sarcasm, : {original_text}")
            comeback = response.text.strip()

            # Post a reply
            self.client.create_tweet(
                text=f"@{tweet.author_id} {comeback}",
                in_reply_to_tweet_id=tweet.id
            )
        except Exception as e:
            print(f"Error responding to mention: {e}")

    def run(self):
        while True:
            mentions = self.check_mentions()
            for tweet in mentions:
                    self.respond_to_mention(tweet)
            time.sleep(60)

# Run the bot
if __name__ == "__main__":
    bot = TwitterBot()
    bot.run()
