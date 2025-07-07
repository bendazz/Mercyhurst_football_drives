#!/usr/bin/env python3
"""
Enhanced script to extract real scoring data from the Mercyhurst vs Wheeling game
This script uses the discovered scoring table structure to create accurate data
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_real_scoring_data():
    """
    Extract real scoring data from the discovered table structure
    """
    url = "https://hurstathletics.com/sports/football/stats/2024/wheeling-university/boxscore/14044"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the scoring table (Table 2 from our earlier discovery)
        tables = soup.find_all('table')
        
        scoring_data = []
        
        for table in tables:
            headers = table.find_all('th')
            if headers:
                header_text = [h.get_text().strip() for h in headers]
                # Look for the scoring table
                if any('Scoring Play' in h for h in header_text):
                    print(f"Found scoring table with headers: {header_text}")
                    
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    mercyhurst_score = 0
                    wheeling_score = 0
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:
                            quarter_time = cells[0].get_text().strip()
                            quarter = cells[1].get_text().strip()
                            time = cells[2].get_text().strip()
                            play = cells[3].get_text().strip()
                            mhu_score = cells[4].get_text().strip()
                            whl_score = cells[5].get_text().strip()
                            
                            # Parse the scores
                            try:
                                mercyhurst_score = int(mhu_score)
                                wheeling_score = int(whl_score)
                            except ValueError:
                                continue
                            
                            # Parse quarter and time
                            quarter_num = parse_quarter(quarter)
                            elapsed_seconds = calculate_elapsed_seconds(quarter_num, time)
                            
                            # Determine which team scored
                            team = "Wheeling" if "WHL" in play else "Mercyhurst"
                            
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
                                "wheeling_score": wheeling_score,
                                "score_differential": mercyhurst_score - wheeling_score
                            })
                    
                    break
        
        return scoring_data
        
    except Exception as e:
        print(f"Error extracting real data: {e}")
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
    """Main function to extract and save real scoring data"""
    print("=== Extracting Real Scoring Data ===")
    
    real_data = scrape_real_scoring_data()
    
    if real_data:
        # Save to JSON file
        with open('/workspaces/Mercyhurst_football_drives/drive_data_real.json', 'w') as f:
            json.dump(real_data, f, indent=2)
        
        print(f"Successfully extracted {len(real_data)} scoring plays!")
        print("\n=== Scoring Summary ===")
        
        for i, play in enumerate(real_data, 1):
            print(f"{i:2d}. Q{play['quarter']} {play['time']} - {play['team']} {play['result']}")
            print(f"    Score: MU {play['mercyhurst_score']} - WU {play['wheeling_score']} (Diff: {play['score_differential']:+d})")
            print(f"    Play: {play['play_description'][:80]}...")
            print()
        
        # Replace the sample data with real data
        import shutil
        shutil.copy('/workspaces/Mercyhurst_football_drives/drive_data_real.json', 
                   '/workspaces/Mercyhurst_football_drives/drive_data.json')
        print("Real data saved as drive_data.json")
    else:
        print("No real data found. Using sample data instead.")

if __name__ == "__main__":
    main()
