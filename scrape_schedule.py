#!/usr/bin/env python3
"""
Script to scrape all Mercyhurst 2024 football games from the schedule page
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

def scrape_schedule():
    """
    Scrape the 2024 schedule page to get all game URLs
    """
    schedule_url = "https://hurstathletics.com/sports/football/schedule/2024"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(schedule_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save the schedule page for analysis
        with open('/workspaces/Mercyhurst_football_drives/schedule_source.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"Schedule page title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for game links
        games = []
        
        # Find all links that might lead to boxscores
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            # Look for boxscore URLs
            if 'boxscore' in href or 'stats' in href:
                # Extract game info
                game_text = link.get_text(strip=True)
                
                # Make sure it's a full URL
                if href.startswith('/'):
                    full_url = f"https://hurstathletics.com{href}"
                else:
                    full_url = href
                
                games.append({
                    'url': full_url,
                    'text': game_text,
                    'link_text': link.get_text(strip=True)
                })
        
        # Also look for any schedule table or game listings
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on schedule page")
        
        # Look for game rows in tables
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 2:  # Skip small tables
                print(f"\nTable {i+1} has {len(rows)} rows")
                
                # Look at first few rows to understand structure
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"  Row {j+1}: {cell_texts}")
                        
                        # Look for links in cells
                        for cell in cells:
                            cell_links = cell.find_all('a', href=True)
                            for cell_link in cell_links:
                                href = cell_link['href']
                                if 'boxscore' in href or 'stats' in href:
                                    if href.startswith('/'):
                                        full_url = f"https://hurstathletics.com{href}"
                                    else:
                                        full_url = href
                                    
                                    games.append({
                                        'url': full_url,
                                        'opponent': cell_link.get_text(strip=True),
                                        'table_row': j
                                    })
        
        print(f"\nFound {len(games)} potential game links:")
        for i, game in enumerate(games[:10]):  # Show first 10
            print(f"{i+1}. {game['url']}")
            print(f"   Text: {game.get('text', game.get('opponent', 'N/A'))}")
        
        return games
        
    except Exception as e:
        print(f"Error scraping schedule: {e}")
        return []

def extract_opponent_and_date(url):
    """
    Extract opponent name and date from the boxscore URL
    """
    try:
        # URL pattern: .../stats/2024/opponent-name/boxscore/id
        parts = url.split('/')
        
        opponent = "Unknown"
        date = "Unknown"
        
        for i, part in enumerate(parts):
            if part == "2024" and i + 1 < len(parts):
                opponent_part = parts[i + 1]
                # Convert URL format to readable name
                opponent = opponent_part.replace('-', ' ').title()
                break
        
        return opponent, date
        
    except Exception as e:
        print(f"Error extracting info from URL {url}: {e}")
        return "Unknown", "Unknown"

def main():
    """
    Main function to scrape the schedule and analyze game links
    """
    print("=== Mercyhurst 2024 Football Schedule Scraper ===")
    
    games = scrape_schedule()
    
    if games:
        # Clean up and organize games
        unique_games = []
        seen_urls = set()
        
        for game in games:
            url = game['url']
            if url not in seen_urls and 'boxscore' in url:
                seen_urls.add(url)
                
                opponent, date = extract_opponent_and_date(url)
                
                unique_games.append({
                    'url': url,
                    'opponent': opponent,
                    'date': date,
                    'display_name': f"vs {opponent}"
                })
        
        print(f"\n=== Found {len(unique_games)} Unique Games ===")
        for i, game in enumerate(unique_games):
            print(f"{i+1:2d}. {game['display_name']}")
            print(f"     URL: {game['url']}")
        
        # Save the game list
        with open('/workspaces/Mercyhurst_football_drives/games_list.json', 'w') as f:
            json.dump(unique_games, f, indent=2)
        
        print(f"\nSaved {len(unique_games)} games to games_list.json")
        
    else:
        print("No games found. Check the schedule page structure.")

if __name__ == "__main__":
    main()
