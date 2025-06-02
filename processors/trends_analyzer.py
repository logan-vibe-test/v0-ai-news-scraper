"""
Trends analyzer for AI Voice News Scraper
Analyzes sentiment trends over the last few runs
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from storage.db_manager import get_recent_runs

logger = logging.getLogger(__name__)

class TrendsAnalyzer:
    """Analyzes trends in sentiment and activity over recent runs"""
    
    def __init__(self):
        pass
    
    def _calculate_sentiment_score(self, sentiment_summary: Dict) -> float:
        """Calculate a numerical sentiment score from sentiment counts"""
        positive = sentiment_summary.get('positive', 0)
        negative = sentiment_summary.get('negative', 0)
        neutral = sentiment_summary.get('neutral', 0)
        
        total = positive + negative + neutral
        if total == 0:
            return 0.0
        
        # Score from -1 (all negative) to +1 (all positive)
        score = (positive - negative) / total
        return score
    
    def _get_trend_direction(self, values: List[float]) -> str:
        """Determine trend direction from a list of values"""
        if len(values) < 2:
            return "stable"
        
        # Calculate the overall trend
        first_half = sum(values[:len(values)//2]) / (len(values)//2) if len(values) >= 2 else values[0]
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        difference = second_half - first_half
        
        if difference > 0.1:
            return "improving"
        elif difference < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _get_trend_emoji(self, direction: str) -> str:
        """Get emoji for trend direction"""
        emoji_map = {
            "improving": "📈",
            "declining": "📉", 
            "stable": "➡️"
        }
        return emoji_map.get(direction, "➡️")
    
    async def analyze_trends(self, current_run_data: Dict) -> Dict:
        """Analyze trends over the last 3 runs including current"""
        try:
            # Get the last 2 runs (we'll add current as the 3rd)
            recent_runs = await get_recent_runs(limit=2)
            
            # Add current run data
            current_summary = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'articles_found': current_run_data.get('articles_found', 0),
                'articles_processed': current_run_data.get('articles_processed', 0),
                'reddit_posts': current_run_data.get('reddit_posts', 0),
                'sentiment_summary': current_run_data.get('sentiment_summary', {}),
                'subreddit_activity': current_run_data.get('subreddit_activity', {})
            }
            
            # Combine all runs (most recent first)
            all_runs = [current_summary] + recent_runs
            
            if len(all_runs) < 2:
                return {
                    'available': False,
                    'message': "Not enough historical data for trend analysis (need at least 2 runs)"
                }
            
            # Analyze sentiment trends
            sentiment_scores = []
            sentiment_details = []
            
            for run in all_runs:
                score = self._calculate_sentiment_score(run.get('sentiment_summary', {}))
                sentiment_scores.append(score)
                
                sentiment_summary = run.get('sentiment_summary', {})
                sentiment_details.append({
                    'date': run.get('date', 'Unknown'),
                    'score': score,
                    'positive': sentiment_summary.get('positive', 0),
                    'negative': sentiment_summary.get('negative', 0),
                    'neutral': sentiment_summary.get('neutral', 0),
                    'total': sum(sentiment_summary.values()) if sentiment_summary else 0
                })
            
            # Analyze activity trends
            activity_scores = [run.get('reddit_posts', 0) for run in all_runs]
            article_scores = [run.get('articles_processed', 0) for run in all_runs]
            
            # Calculate trends
            sentiment_trend = self._get_trend_direction(sentiment_scores)
            activity_trend = self._get_trend_direction(activity_scores)
            news_trend = self._get_trend_direction(article_scores)
            
            # Calculate changes
            sentiment_change = sentiment_scores[0] - sentiment_scores[-1] if len(sentiment_scores) >= 2 else 0
            activity_change = activity_scores[0] - activity_scores[-1] if len(activity_scores) >= 2 else 0
            news_change = article_scores[0] - article_scores[-1] if len(article_scores) >= 2 else 0
            
            # Analyze most active subreddits
            subreddit_trends = self._analyze_subreddit_trends(all_runs)
            
            # Generate insights
            insights = self._generate_insights(sentiment_trend, activity_trend, news_trend, 
                                            sentiment_change, activity_change, news_change)
            
            return {
                'available': True,
                'runs_analyzed': len(all_runs),
                'date_range': f"{all_runs[-1].get('date', 'Unknown')} to {all_runs[0].get('date', 'Unknown')}",
                'sentiment': {
                    'trend': sentiment_trend,
                    'emoji': self._get_trend_emoji(sentiment_trend),
                    'change': sentiment_change,
                    'current_score': sentiment_scores[0],
                    'details': sentiment_details
                },
                'activity': {
                    'trend': activity_trend,
                    'emoji': self._get_trend_emoji(activity_trend),
                    'change': activity_change,
                    'current_posts': activity_scores[0],
                    'details': activity_scores
                },
                'news_volume': {
                    'trend': news_trend,
                    'emoji': self._get_trend_emoji(news_trend),
                    'change': news_change,
                    'current_articles': article_scores[0],
                    'details': article_scores
                },
                'subreddit_trends': subreddit_trends,
                'insights': insights,
                'summary': self._generate_summary(sentiment_trend, activity_trend, news_trend)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {
                'available': False,
                'error': str(e),
                'message': "Error occurred during trend analysis"
            }
    
    def _analyze_subreddit_trends(self, runs: List[Dict]) -> Dict:
        """Analyze which subreddits are most/least active"""
        subreddit_activity = {}
        
        for run in runs:
            activity = run.get('subreddit_activity', {})
            for subreddit, count in activity.items():
                if subreddit not in subreddit_activity:
                    subreddit_activity[subreddit] = []
                subreddit_activity[subreddit].append(count)
        
        # Calculate trends for each subreddit
        subreddit_trends = {}
        for subreddit, counts in subreddit_activity.items():
            if len(counts) >= 2:
                trend = self._get_trend_direction(counts)
                avg_activity = sum(counts) / len(counts)
                subreddit_trends[subreddit] = {
                    'trend': trend,
                    'emoji': self._get_trend_emoji(trend),
                    'avg_posts': avg_activity,
                    'current_posts': counts[0] if counts else 0
                }
        
        # Sort by average activity
        sorted_subreddits = sorted(subreddit_trends.items(), 
                                 key=lambda x: x[1]['avg_posts'], reverse=True)
        
        return dict(sorted_subreddits[:5])  # Top 5 most active
    
    def _generate_insights(self, sentiment_trend: str, activity_trend: str, news_trend: str,
                          sentiment_change: float, activity_change: float, news_change: float) -> List[str]:
        """Generate human-readable insights from trends"""
        insights = []
        
        # Sentiment insights
        if sentiment_trend == "improving":
            insights.append("🎉 Community sentiment is becoming more positive")
        elif sentiment_trend == "declining":
            insights.append("⚠️ Community sentiment is becoming more negative")
        else:
            insights.append("😐 Community sentiment remains stable")
        
        # Activity insights
        if activity_trend == "improving":
            insights.append("📈 Reddit discussion activity is increasing")
        elif activity_trend == "declining":
            insights.append("📉 Reddit discussion activity is decreasing")
        
        # News insights
        if news_trend == "improving":
            insights.append("📰 More voice AI news articles are being published")
        elif news_trend == "declining":
            insights.append("📰 Fewer voice AI news articles are being published")
        
        # Combined insights
        if sentiment_trend == "improving" and activity_trend == "improving":
            insights.append("🚀 Both sentiment and activity are trending positively!")
        elif sentiment_trend == "declining" and activity_trend == "declining":
            insights.append("🔍 Both sentiment and activity are declining - worth monitoring")
        
        return insights
    
    def _generate_summary(self, sentiment_trend: str, activity_trend: str, news_trend: str) -> str:
        """Generate a brief summary of all trends"""
        trends = [
            f"Sentiment: {sentiment_trend}",
            f"Activity: {activity_trend}", 
            f"News: {news_trend}"
        ]
        return " | ".join(trends)

# Global instance
trends_analyzer = TrendsAnalyzer()

async def analyze_current_trends(current_run_data: Dict) -> Dict:
    """Analyze trends for the current run"""
    return await trends_analyzer.analyze_trends(current_run_data)
