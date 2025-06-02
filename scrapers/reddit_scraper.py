import asyncio
import os
import random
import re
from typing import Dict, List, Optional

import praw
import spacy
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()

# Initialize spaCy and SentimentIntensityAnalyzer
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model for spaCy...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

sid = SentimentIntensityAnalyzer()


class RedditScraper:
    """
    A class to scrape Reddit for top posts, summarize them using AI,
    and perform sentiment analysis.
    """

    def __init__(self):
        """
        Initializes the RedditScraper with Reddit API credentials
        from environment variables.
        """
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
        )

    def get_top_posts(self, subreddit_name: str, limit: int = 5) -> List[praw.models.Submission]:
        """
        Fetches the top posts from a specified subreddit.

        Args:
            subreddit_name (str): The name of the subreddit to scrape.
            limit (int): The number of top posts to retrieve.

        Returns:
            List[praw.models.Submission]: A list of Submission objects representing the top posts.
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        top_posts = list(subreddit.hot(limit=limit))  # Use .hot() for top posts
        return top_posts

    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Summarizes a given text using spaCy's NLP capabilities.

        Args:
            text (str): The text to be summarized.
            max_length (int): The maximum length of the summary.

        Returns:
            str: A summarized version of the input text.
        """
        doc = nlp(text)
        sentences = list(doc.sents)
        summary = " ".join(str(s) for s in sentences[:3])  # Simple: first 3 sentences
        summary = summary[:max_length] + "..." if len(summary) > max_length else summary
        return summary

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Performs sentiment analysis on a given text using NLTK's VADER.

        Args:
            text (str): The text to be analyzed.

        Returns:
            Dict: A dictionary containing sentiment scores (positive, negative, neutral, compound).
        """
        scores = sid.polarity_scores(text)
        return scores

    def clean_text(self, text: str) -> str:
        """
        Cleans the text by removing URLs, mentions, and special characters.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: A cleaned version of the input text.
        """
        text = re.sub(r"http\S+|www\S+|@\S+", "", text)  # Remove URLs and mentions
        text = re.sub(r"[^a-zA-Z\s]", "", text)  # Remove special characters
        return text

    async def scrape_reddit(self, news_items: Optional[List] = None) -> List[Dict]:
        """
        Scrapes Reddit for top posts, summarizes them, and performs sentiment analysis.

        Args:
            news_items: Optional list of news items (not used, kept for compatibility)

        Returns:
            List[Dict]: A list of dictionaries, each containing information about a scraped post.
        """
        subreddit_name = "news"  # You can change this to any subreddit
        top_posts = self.get_top_posts(subreddit_name, limit=5)
        scraped_data = []

        for post in top_posts:
            cleaned_title = self.clean_text(post.title)
            summary = self.summarize_text(cleaned_title)
            sentiment_scores = self.analyze_sentiment(cleaned_title)

            post_data = {
                "title": post.title,
                "summary": summary,
                "sentiment": sentiment_scores,
                "url": post.url,
                "upvotes": post.score,
            }
            scraped_data.append(post_data)

        return scraped_data


_reddit_scraper = RedditScraper()


# Main function for compatibility with existing code
async def scrape_reddit(news_items: Optional[List] = None) -> List[Dict]:
    """
    Scrape Reddit for top posts with summaries and sentiment analysis - SSL FIXED
    
    Args:
        news_items: Optional list of news items (not used, kept for compatibility)
        
    Returns:
        List of top Reddit posts with AI-generated summaries and sentiment
    """
    return await _reddit_scraper.scrape_reddit(news_items)
