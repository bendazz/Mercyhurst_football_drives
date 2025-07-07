#!/usr/bin/env python3
"""
Script to fix drive data issues:
1. Ensure all games have proper start/end points
2. Fix score differential calculation to always be Mercyhurst - Opponent
3. Fix team attribution based on play descriptions
"""

import json
import os
import re
from pathlib import Path

def fix_team_attribution(play_description, current_team):
    """
    Fix team attribution based on play description
    Returns the correct team name
    """
    if not play_description:
        return current_team
    
    # Look for team abbreviations in play descriptions
    if play_description.startswith('MER -') or play_description.startswith('MERC -'):
        return 'Mercyhurst'
    elif play_description.startswith('WHL -'):
        return 'Wheeling University'
    elif play_description.startswith('HOW -'):
        return 'Howard University'
    elif play_description.startswith('RMU -'):
        return 'Robert Morris University'
    elif play_description.startswith('MSU -'):
        return 'Montana State University'
    elif play_description.startswith('FSU -'):
        return 'Frostburg State University'
    elif play_description.startswith('BUFF -'):
        return 'Buffalo State'
    elif play_description.startswith('CCSU -'):
        return 'Central Connecticut State University'
    elif play_description.startswith('SHU -'):
        return 'Sacred Heart University'
    elif play_description.startswith('SHIP -'):
        return 'Shippensburg University'
    elif play_description.startswith('SLIPP -'):
        return 'Slippery Rock University'
    
    # If no clear indicator, return current team
    return current_team

def ensure_game_boundaries(drives, opponent_name):
    """
    Ensure game has proper start and end points
    """
    if not drives:
        return drives
    
    # Check if first drive is game start
    if drives[0]['team'] != 'Game Start':
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
        drives.insert(0, game_start)
    
    # Check if last drive is game end
    if drives[-1]['team'] != 'Game End':
        final_drive = drives[-1]
        game_end = {
            "quarter": 4,
            "time": "00:00",
            "elapsed_seconds": 3600,
            "team": "Game End",
            "result": "Game End",
            "play_description": f"Final Score - Mercyhurst {final_drive['mercyhurst_score']}, {opponent_name} {final_drive['opponent_score']}",
            "mercyhurst_score": final_drive['mercyhurst_score'],
            "opponent_score": final_drive['opponent_score'],
            "score_differential": final_drive['mercyhurst_score'] - final_drive['opponent_score']
        }
        drives.append(game_end)
    
    return drives

def fix_score_differential(drives):
    """
    Ensure score differential is always Mercyhurst - Opponent
    """
    for drive in drives:
        # Recalculate score differential
        drive['score_differential'] = drive['mercyhurst_score'] - drive['opponent_score']
    
    return drives

def fix_game_data(file_path, opponent_name):
    """
    Fix a single game data file
    """
    try:
        with open(file_path, 'r') as f:
            drives = json.load(f)
        
        print(f"Processing {opponent_name}...")
        print(f"  Original drives: {len(drives)}")
        
        # Fix team attribution based on play descriptions
        for drive in drives:
            if drive['team'] not in ['Game Start', 'Game End']:
                corrected_team = fix_team_attribution(drive['play_description'], drive['team'])
                if corrected_team != drive['team']:
                    print(f"  Fixed team attribution: {drive['team']} -> {corrected_team}")
                    drive['team'] = corrected_team
        
        # Ensure game boundaries
        drives = ensure_game_boundaries(drives, opponent_name)
        
        # Fix score differential
        drives = fix_score_differential(drives)
        
        print(f"  Final drives: {len(drives)}")
        print(f"  Final score: Mercyhurst {drives[-1]['mercyhurst_score']} - {opponent_name} {drives[-1]['opponent_score']}")
        print(f"  Final differential: {drives[-1]['score_differential']}")
        
        # Save the fixed data
        with open(file_path, 'w') as f:
            json.dump(drives, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """
    Main function to fix all game data files
    """
    print("=== Fixing Drive Data Issues ===")
    
    games_dir = Path('/workspaces/Mercyhurst_football_drives/games_data')
    
    if not games_dir.exists():
        print("Games data directory not found!")
        return
    
    # Load games index to get opponent names
    try:
        with open('/workspaces/Mercyhurst_football_drives/games_index.json', 'r') as f:
            games_index = json.load(f)
    except Exception as e:
        print(f"Error loading games index: {e}")
        return
    
    fixed_count = 0
    total_count = 0
    
    for game in games_index['games']:
        opponent = game['opponent']
        filename = f"game_{opponent.lower().replace(' ', '_')}.json"
        file_path = games_dir / filename
        
        if file_path.exists():
            total_count += 1
            if fix_game_data(file_path, opponent):
                fixed_count += 1
        else:
            print(f"File not found: {filename}")
    
    print(f"\n=== Summary ===")
    print(f"Fixed {fixed_count} out of {total_count} games")

if __name__ == "__main__":
    main()
