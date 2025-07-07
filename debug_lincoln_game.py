#!/usr/bin/env python3
"""
Debug script to check the Lincoln University game data structure
"""

import requests
from bs4 import BeautifulSoup

def debug_lincoln_game():
    """
    Debug the Lincoln University game to understand the scoring table structure
    """
    # Lincoln University game URL
    url = "https://hurstathletics.com/sports/football/stats/2024/lincoln-university/boxscore/14053"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        print(f"Found {len(tables)} tables on the page")
        
        for i, table in enumerate(tables):
            headers = table.find_all('th')
            if headers:
                header_text = [h.get_text().strip() for h in headers]
                print(f"\nTable {i+1} headers: {header_text}")
                
                # Look for the scoring table
                if any('Scoring Play' in h or 'Score' in h for h in header_text):
                    print(f"*** This looks like the scoring table! ***")
                    
                    # Get first few rows to understand structure
                    rows = table.find_all('tr')
                    print(f"Table has {len(rows)} rows")
                    
                    for j, row in enumerate(rows[:5]):  # Show first 5 rows
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            cell_texts = [cell.get_text().strip() for cell in cells]
                            print(f"  Row {j+1}: {cell_texts}")
                            
        # Also look for final score information
        print("\n=== Looking for final score information ===")
        
        # Check for score elements
        score_elements = soup.find_all(text=lambda text: text and ('66' in text or '0' in text))
        for elem in score_elements[:10]:  # Show first 10 matches
            if elem.strip():
                print(f"Found text with score: '{elem.strip()}'")
                parent = elem.parent
                if parent:
                    print(f"  Parent element: {parent.name} - {parent.get('class', 'no class')}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_lincoln_game()
