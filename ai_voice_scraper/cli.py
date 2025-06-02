#!/usr/bin/env python
"""
Command-line interface for AI Voice News Scraper
"""
import asyncio
import logging
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components
from ai_voice_scraper.core.pipeline import run_pipeline
from ai_voice_scraper.utils.logging import setup_logging

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='AI Voice News Scraper')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    parser.add_argument('--no-email', action='store_true',
                        help='Skip sending email digest')
    parser.add_argument('--no-slack', action='store_true',
                        help='Skip sending Slack notifications')
    parser.add_argument('--test', action='store_true',
                        help='Run in test mode (limited API calls)')
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Run the main pipeline
    try:
        options = {
            'skip_email': args.no_email,
            'skip_slack': args.no_slack,
            'test_mode': args.test
        }
        
        results = asyncio.run(run_pipeline(logger, options))
        
        if "error" in results:
            print(f"\n❌ Error: {results['error']}")
            return 1
        
        print("\n📊 Results:")
        print(f"  Articles found: {results['articles_found']}")
        print(f"  Articles processed: {results['articles_processed']} (relevant to voice AI)")
        print(f"  Reddit posts found: {results['reddit_posts']}")
        return 0
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
