import os
import tweepy
import time
import google.generativeai as genai
from dotenv import load_dotenv
from config.x_config import api


load_dotenv()


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 50,
  "response_mime_type": "text/plain",
}


def cook(tweet):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
    history=[
    ]
    )

    response = chat_session.send_message(f"roast this person's tweet: {tweet}")
    return response.text.strip()



class MyStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        try:
            # Log the incoming tweet
            print(f"New tweet from {tweet.author_id}: {tweet.text}")

            # Check if the bot is mentioned
            if '@seuncook' in tweet.text:
                # Fetch the original tweet
                original_tweet_id = tweet.referenced_tweets[0].id
                original_tweet = api.get_status(original_tweet_id)
                original_text = original_tweet.text

                # Generate a response using Gemini AI
                comeback = cook()

                # Reply to the original tweet with the generated roast
                api.update_status(
                    f"@{original_tweet.user.screen_name} {comeback}",
                    in_reply_to_status_id=original_tweet_id
                )
        except tweepy.TweepyException as e:
            if e.api_code == 187:
                print("Error: Duplicate status.")
            elif e.api_code == 88:
                print("Error: Rate limit exceeded. Sleeping for 15 minutes.")
                time.sleep(15 * 60)
            else:
                print(f"TweepyException: {e}")
        except (genai.exceptions.APIError, genai.exceptions.RequestError) as e:
            print(f"Gemini API Error: {e}")
        except (ConnectionError, TimeoutError) as e:
            print(f"Network error: {e}. Retrying in 5 seconds.")
            time.sleep(5)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            pass



# Initialize and start the stream
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
stream = MyStream(bearer_token=bearer_token)

stream.add_rules(tweepy.StreamRule("@seuncook"))
stream.filter()
