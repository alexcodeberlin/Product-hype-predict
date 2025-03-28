import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import tweepy
from tweepy.errors import TooManyRequests

# Secure Bearer Token
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAC3H0AEAAAAAtpKfJ9410cXvoXPf3zsWg2mwPFU%3DwtjZJZcMPSm7UuvlLK8BzReihqz85txuu0d86M8smRPdeDCVsx"

# Authenticate using OAuth 2.0
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Fetch tweets with filtering for user followers count
def fetch_twitter_data(client, product, max_tweets=10, min_followers=0):
    """Fetch recent tweets about a product with optional follower filtering."""
    print(f"\n🔍 Fetching up to {max_tweets} tweets about '{product}' (Min Followers: {min_followers})...\n")

    tweets_data = []

    try:
        response = client.search_recent_tweets(
            query=f"{product} lang:en -is:retweet",
            max_results=max_tweets,
            tweet_fields=["created_at", "public_metrics", "author_id"],
            user_fields=["location", "public_metrics"],
            expansions=["author_id"]
        )

        if not response.data:
            print("❌ No tweets found.")
            return pd.DataFrame()

        # Get user details
        users = {user.id: {"location": user.location, "followers": user.public_metrics["followers_count"]}
                 for user in response.includes.get("users", [])}

        for tweet in response.data:
            user_info = users.get(tweet.author_id, {"location": "Unknown", "followers": 0})

            if user_info["followers"] >= min_followers:  # Filter by followers
                sentiment = TextBlob(tweet.text).sentiment.polarity

                tweets_data.append({
                    "tweet_id": tweet.id,
                    "timestamp": tweet.created_at,
                    "text": tweet.text,
                    "sentiment_score": sentiment,
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "user_location": user_info["location"],
                    "followers": user_info["followers"]
                })

    except TooManyRequests as e:
        reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time()))
        wait_time = max(0, reset_time - int(time.time()) + 1)
        print(f"🚨 Rate limit exceeded! Waiting {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return fetch_twitter_data(client, product, max_tweets, min_followers)

    return pd.DataFrame(tweets_data)

# Save Twitter data to CSV
def save_twitter_data_to_csv(df, filename):
    """Save tweet data to a CSV file."""
    if df.empty:
        print("❌ No data to save.")
        return
    df.to_csv(filename, index=False)
    print(f"✅ Saved Twitter data to {filename}")

# Plot likes and retweets over time
def plot_twitter_engagement(df, title):
    """Plot likes and retweets trends over time."""
    if df.empty:
        print("❌ No data to plot.")
        return

    plt.figure(figsize=(10, 5))
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    plt.plot(df["timestamp"], df["likes"], marker='o', linestyle='-', color='blue', label="Likes")
    plt.plot(df["timestamp"], df["retweets"], marker='s', linestyle='-', color='red', label="Retweets")

    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title(f"📈 Tweet Engagement - {title}")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.show()

# Run the script
if __name__ == "__main__":
    product = "iPhone"

    # First request: Fetch general tweets
    general_tweets = fetch_twitter_data(client, product)
    save_twitter_data_to_csv(general_tweets, f"{product}_general_tweets1.csv")
    plot_twitter_engagement(general_tweets, "All Users")

    # Second request: Fetch tweets from users with 500,000+ followers
    influencer_tweets = fetch_twitter_data(client, product, min_followers=10000)
    save_twitter_data_to_csv(influencer_tweets, f"{product}_influencer_tweets1.csv")
    plot_twitter_engagement(influencer_tweets, "Influencers (500K+ Followers)")
