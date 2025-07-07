#!/usr/bin/env python3
"""
Test script to verify web scraping functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import GameDataScraper

def test_scraping():
    """Test the web scraping functionality"""
    print("Testing Mercyhurst vs Wheeling game data scraping...")
    
    url = "https://hurstathletics.com/sports/football/stats/2024/wheeling-university/boxscore/14044"
    scraper = GameDataScraper(url)
    
    try:
        game_data = scraper.scrape_play_by_play()
        
        print(f"\nFound {len(game_data)} scoring events:")
        print("-" * 60)
        
        for i, event in enumerate(game_data, 1):
            print(f"{i}. Time: {event.get('time', 'N/A')}")
            print(f"   Quarter: {event.get('quarter', 'N/A')}")
            print(f"   Elapsed: {event.get('elapsed_seconds', 0)} seconds")
            print(f"   Score: Mercyhurst {event.get('mercyhurst_score', 0)} - Wheeling {event.get('wheeling_score', 0)}")
            print(f"   Differential: {event.get('score_differential', 0)}")
            print(f"   Play: {event.get('play', 'N/A')[:50]}...")
            print()
        
        if game_data:
            final_event = game_data[-1]
            print(f"Final Score: Mercyhurst {final_event.get('mercyhurst_score', 0)} - Wheeling {final_event.get('wheeling_score', 0)}")
            print(f"Final Differential: {final_event.get('score_differential', 0)}")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("This is expected if the website structure has changed or if there are network issues.")
        print("The application will fall back to sample data for demonstration.")

if __name__ == "__main__":
    test_scraping()
