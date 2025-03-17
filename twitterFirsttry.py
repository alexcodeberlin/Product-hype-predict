import random
import time
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
import tweepy
from textblob import TextBlob
from tweepy.errors import TooManyRequests


# Use only the Bearer Token
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIawzwEAAAAAmdd1uV6UbfTX2P7Pmo6hY1Nqklw%3DBVKzB3gqkIdlKBXg21mVfMYmDXb86TfD7CxM0gtEY9PWgnWHlh"

# Authenticate using OAuth 2.0
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Fetch recent tweets about the product
def fetch_twitter_data(client, product, max_tweets=100):
    """Fetch Twitter data related to the product."""
    print(f"Fetching tweets about '{product}'...")
    
    tweets_data = []
    backoff_time = 60  # Start with 1-minute backoff time

    while len(tweets_data) < max_tweets:
        try:
            # Fetch 100 tweets at a time
            response = client.search_recent_tweets(query=product, max_results=100, tweet_fields=["created_at", "public_metrics", "author_id"])
            
            # Process the fetched tweets
            for tweet in response.data:
                sentiment = TextBlob(tweet.text).sentiment.polarity  # Basic sentiment score
                
                # Fetch user details using the author's ID
                user = client.get_user(id=tweet.author_id)
                
                # Append the tweet data including user location if available
                tweets_data.append({
                    "tweet_id": tweet.id,
                    "timestamp": tweet.created_at,
                    "user_location": user.location if user.location else "Unknown",  # Get location from user profile
                    "text": tweet.text,
                    "sentiment_score": sentiment,
                    "likes": tweet.public_metrics['like_count'],
                    "retweets": tweet.public_metrics['retweet_count']
                })
            
            # If we have fetched enough tweets, break the loop
            if len(tweets_data) >= max_tweets:
                break

        except TooManyRequests as e:
            # Handle rate limit by waiting until the retry time
            print(f"Rate limit exceeded. Retrying after {e.response.headers['x-rate-limit-reset']} seconds.")
            retry_after = int(e.response.headers['x-rate-limit-reset']) - int(time.time()) + 1
            time.sleep(retry_after)

    df = pd.DataFrame(tweets_data)
    return df

# Save Twitter data to CSV
def save_twitter_data_to_csv(df, product):
    """Save tweet data to a CSV file."""
    filename = f"{product}_twitter_data.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Saved Twitter data to {filename}")

# Plot likes and retweets over time
def plot_twitter_engagement(df, product):
    """Plot likes and retweets trends over time."""
    plt.figure(figsize=(10, 5))

    # Convert 'timestamp' to datetime for better plotting
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Plot likes
    plt.plot(df["timestamp"], df["likes"], marker='o', linestyle='-', color='blue', label="Likes")
    
    # Plot retweets
    plt.plot(df["timestamp"], df["retweets"], marker='s', linestyle='-', color='red', label="Retweets")

    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title(f"Tweet Engagement for '{product}'")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.show()

# Run the script
if __name__ == "__main__":
    product = "iPhone"  # Change this to any product

    # Fetch Twitter data
    twitter_data = fetch_twitter_data(client, product)

    # Save to CSV
    save_twitter_data_to_csv(twitter_data, product)

    # Plot engagement trends
    plot_twitter_engagement(twitter_data, product)
