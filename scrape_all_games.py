#!/usr/bin/env python3
"""
Script to scrape scoring data from all Mercyhurst 2024 football games
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
import time

def load_games_list():
    """
    Load the list of games from games_list.json
    """
    try:
        with open('/workspaces/Mercyhurst_football_drives/games_list.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("games_list.json not found. Run scrape_schedule.py first.")
        return []

def scrape_game_scoring_data(game_url, opponent_name):
    """
    Extract scoring data from a single game's boxscore page
    """
    try:
        print(f"Scraping {opponent_name}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(game_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the scoring table
        tables = soup.find_all('table')
        
        scoring_data = []
        
        for table in tables:
            headers = table.find_all('th')
            if headers:
                header_text = [h.get_text().strip() for h in headers]
                # Look for the scoring table
                if any('Scoring Play' in h for h in header_text):
                    print(f"  Found scoring table for {opponent_name}")
                    print(f"  Headers: {header_text}")
                    
                    # Find the column indices for Mercyhurst and opponent scores
                    mercyhurst_col = -1
                    opponent_col = -1
                    
                    for i, header in enumerate(header_text):
                        if header in ['MER', 'MHU', 'MERC', 'MCY']:
                            mercyhurst_col = i
                        elif header not in ['Qtr. - Time', 'Qtr', 'Time', 'Scoring Play', 'MER', 'MHU', 'MERC', 'MCY']:
                            # This should be the opponent column
                            opponent_col = i
                    
                    if mercyhurst_col == -1 or opponent_col == -1:
                        print(f"  Could not identify score columns for {opponent_name}")
                        continue
                    
                    print(f"  Mercyhurst score column: {mercyhurst_col} ({header_text[mercyhurst_col]})")
                    print(f"  Opponent score column: {opponent_col} ({header_text[opponent_col]})")
                    
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    mercyhurst_score = 0
                    opponent_score = 0
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) > max(mercyhurst_col, opponent_col):
                            quarter_time = cells[0].get_text().strip()
                            quarter = cells[1].get_text().strip()
                            time = cells[2].get_text().strip()
                            play = cells[3].get_text().strip()
                            mhu_score = cells[mercyhurst_col].get_text().strip()
                            opp_score = cells[opponent_col].get_text().strip()
                            
                            # Parse the scores
                            try:
                                mercyhurst_score = int(mhu_score)
                                opponent_score = int(opp_score)
                            except ValueError:
                                continue
                            
                            # Parse quarter and time
                            quarter_num = parse_quarter(quarter)
                            elapsed_seconds = calculate_elapsed_seconds(quarter_num, time)
                            
                            # Determine which team scored
                            team = "Mercyhurst" if ("MHU" in play or "MER" in play or "MCY" in play) else opponent_name
                            
                            # Determine scoring type
                            result = "Touchdown"
                            if "field goal" in play.lower() or "FG" in play:
                                result = "Field Goal"
                            elif "safety" in play.lower():
                                result = "Safety"
                            
                            scoring_data.append({
                                "quarter": quarter_num,
                                "time": time,
                                "elapsed_seconds": elapsed_seconds,
                                "team": team,
                                "result": result,
                                "play_description": play,
                                "mercyhurst_score": mercyhurst_score,
                                "opponent_score": opponent_score,
                                "score_differential": mercyhurst_score - opponent_score
                            })
                    
                    break
        
        if scoring_data:
            # Add game start and end points
            final_mercyhurst = scoring_data[-1]['mercyhurst_score']
            final_opponent = scoring_data[-1]['opponent_score']
            final_differential = final_mercyhurst - final_opponent
            
            # Game start
            game_start = {
                "quarter": 1,
                "time": "15:00",
                "elapsed_seconds": 0,
                "team": "Game Start",
                "result": "Game Start",
                "play_description": f"Game Start - Mercyhurst vs {opponent_name}",
                "mercyhurst_score": 0,
                "opponent_score": 0,
                "score_differential": 0
            }
            
            # Game end
            game_end = {
                "quarter": 4,
                "time": "00:00",
                "elapsed_seconds": 3600,
                "team": "Game End",
                "result": "Game End",
                "play_description": f"Final Score - Mercyhurst {final_mercyhurst}, {opponent_name} {final_opponent}",
                "mercyhurst_score": final_mercyhurst,
                "opponent_score": final_opponent,
                "score_differential": final_differential
            }
            
            # Combine all data
            complete_data = [game_start] + scoring_data + [game_end]
            
            print(f"  Successfully scraped {len(complete_data)} events for {opponent_name}")
            print(f"  Final Score: Mercyhurst {final_mercyhurst} - {opponent_name} {final_opponent}")
            
            return complete_data
        else:
            print(f"  No scoring data found for {opponent_name}")
            return []
            
    except Exception as e:
        print(f"  Error scraping {opponent_name}: {e}")
        return []

def parse_quarter(quarter_str):
    """Parse quarter string to number"""
    if "1st" in quarter_str:
        return 1
    elif "2nd" in quarter_str:
        return 2
    elif "3rd" in quarter_str:
        return 3
    elif "4th" in quarter_str:
        return 4
    else:
        return 1

def calculate_elapsed_seconds(quarter, time_str):
    """Calculate elapsed seconds from quarter and time"""
    try:
        # Parse time like "12:58"
        time_parts = time_str.split(':')
        if len(time_parts) == 2:
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])
            
            # Time remaining in quarter
            time_remaining = minutes * 60 + seconds
            
            # Calculate elapsed time
            quarter_start = (quarter - 1) * 15 * 60  # 15 minutes per quarter
            elapsed = quarter_start + (15 * 60 - time_remaining)
            
            return elapsed
    except:
        pass
    
    return 0

def main():
    """
    Main function to scrape all games
    """
    print("=== Scraping All Mercyhurst 2024 Football Games ===")
    
    games = load_games_list()
    
    if not games:
        print("No games found. Make sure games_list.json exists.")
        return
    
    # Create directory for all games data
    games_dir = '/workspaces/Mercyhurst_football_drives/games_data'
    os.makedirs(games_dir, exist_ok=True)
    
    all_games_data = {}
    successful_games = []
    
    for i, game in enumerate(games, 1):
        print(f"\n[{i}/{len(games)}] Processing {game['opponent']}...")
        
        # Scrape the game data
        game_data = scrape_game_scoring_data(game['url'], game['opponent'])
        
        if game_data:
            # Save individual game data
            filename = f"game_{game['opponent'].lower().replace(' ', '_')}.json"
            filepath = os.path.join(games_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(game_data, f, indent=2)
            
            # Add to master collection
            all_games_data[game['opponent']] = {
                'data': game_data,
                'url': game['url'],
                'opponent': game['opponent'],
                'filename': filename
            }
            
            successful_games.append(game)
            print(f"  ✓ Saved to {filename}")
        else:
            print(f"  ✗ Failed to scrape {game['opponent']}")
        
        # Be respectful - small delay between requests
        time.sleep(1)
    
    # Save master games index
    games_index = {
        'total_games': len(successful_games),
        'successful_games': len(successful_games),
        'games': successful_games,
        'last_updated': datetime.now().isoformat()
    }
    
    with open('/workspaces/Mercyhurst_football_drives/games_index.json', 'w') as f:
        json.dump(games_index, f, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Total games attempted: {len(games)}")
    print(f"Successfully scraped: {len(successful_games)}")
    print(f"Games data saved to: {games_dir}/")
    print(f"Master index saved to: games_index.json")
    
    # Show summary of each game
    print(f"\n=== Game Results Summary ===")
    for game_key, game_info in all_games_data.items():
        game_data = game_info['data']
        final_event = game_data[-1]
        print(f"{game_key:<25} MU {final_event['mercyhurst_score']:2d} - {final_event['opponent_score']:2d} {game_key} (Diff: {final_event['score_differential']:+d})")

if __name__ == "__main__":
    main()
