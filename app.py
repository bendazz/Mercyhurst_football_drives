#!/usr/bin/env python3
"""
Flask web application for visualizing Mercyhurst football drive data
Supports multiple games from the 2024 season
"""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.utils
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def load_games_index():
    """
    Load the index of all available games
    """
    try:
        with open('/workspaces/Mercyhurst_football_drives/games_index.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Games index file not found. Please run scrape_all_games.py first.")
        return {}
    except Exception as e:
        print(f"Error loading games index: {e}")
        return {}

def load_game_data(opponent_name):
    """
    Load drive data for a specific game
    """
    try:
        # Convert opponent name to filename format
        filename = f"game_{opponent_name.lower().replace(' ', '_')}.json"
        filepath = f'/workspaces/Mercyhurst_football_drives/games_data/{filename}'
        
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Game data file not found for {opponent_name}")
        return []
    except Exception as e:
        print(f"Error loading game data for {opponent_name}: {e}")
        return []

def create_score_differential_plot(drive_data, opponent_name):
    """
    Create a Plotly graph showing score differential over time
    """
    if not drive_data:
        return None
    
    # Extract data for plotting
    elapsed_times = [drive['elapsed_seconds'] / 60 for drive in drive_data]  # Convert to minutes
    differentials = [drive['score_differential'] for drive in drive_data]
    mercyhurst_scores = [drive['mercyhurst_score'] for drive in drive_data]
    opponent_scores = [drive['opponent_score'] for drive in drive_data]
    teams = [drive['team'] for drive in drive_data]
    results = [drive['result'] for drive in drive_data]
    
    # Create the plot
    fig = go.Figure()
    
    # Add the main line
    fig.add_trace(go.Scatter(
        x=elapsed_times,
        y=differentials,
        mode='lines+markers',
        name='Score Differential',
        line=dict(color='#003366', width=3),  # Mercyhurst blue
        marker=dict(size=8, color='#003366'),
        hovertemplate='<b>Time:</b> %{x:.1f} minutes<br>' +
                     '<b>Differential:</b> %{y}<br>' +
                     '<b>Score:</b> MU %{customdata[0]} - %{customdata[1]}<br>' +
                     '<b>Drive:</b> %{customdata[2]} %{customdata[3]}<extra></extra>',
        customdata=list(zip(mercyhurst_scores, opponent_scores, teams, results))
    ))
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Mercyhurst vs {opponent_name} - Score Differential Over Time<br>2024 Season',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#003366'}
        },
        xaxis_title='Elapsed Time (minutes)',
        yaxis_title=f'Score Differential (Mercyhurst - {opponent_name})',
        template='plotly_white',
        hovermode='x unified',
        width=1200,
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add quarter markers
    quarter_times = [0, 15, 30, 45, 60]  # 15 minutes per quarter
    quarter_labels = ['Start', 'Q2', 'Q3', 'Q4', 'End']
    
    for i, (time, label) in enumerate(zip(quarter_times, quarter_labels)):
        if time <= max(elapsed_times) and i > 0:
            fig.add_vline(x=time, line_dash="dot", line_color="red", opacity=0.3)
            fig.add_annotation(
                x=time,
                y=max(differentials) + 2,
                text=label,
                showarrow=False,
                font=dict(size=12, color="red")
            )
    
    return fig

def get_game_summary(drive_data, opponent_name):
    """
    Generate a summary of the game from drive data
    """
    if not drive_data:
        return {}
    
    final_drive = drive_data[-1]
    
    # Count drives by team
    mercyhurst_drives = len([d for d in drive_data if d['team'] == 'Mercyhurst'])
    opponent_drives = len([d for d in drive_data if d['team'] == opponent_name])
    
    # Count scoring types
    mercyhurst_tds = len([d for d in drive_data if d['team'] == 'Mercyhurst' and d['result'] == 'Touchdown'])
    mercyhurst_fgs = len([d for d in drive_data if d['team'] == 'Mercyhurst' and d['result'] == 'Field Goal'])
    opponent_tds = len([d for d in drive_data if d['team'] == opponent_name and d['result'] == 'Touchdown'])
    opponent_fgs = len([d for d in drive_data if d['team'] == opponent_name and d['result'] == 'Field Goal'])
    
    return {
        'opponent_name': opponent_name,
        'final_score': {
            'mercyhurst': final_drive['mercyhurst_score'],
            'opponent': final_drive['opponent_score']
        },
        'final_differential': final_drive['score_differential'],
        'total_drives': len(drive_data),
        'mercyhurst_drives': mercyhurst_drives,
        'opponent_drives': opponent_drives,
        'scoring_breakdown': {
            'mercyhurst': {'touchdowns': mercyhurst_tds, 'field_goals': mercyhurst_fgs},
            'opponent': {'touchdowns': opponent_tds, 'field_goals': opponent_fgs}
        }
    }

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/games')
def get_games():
    """API endpoint to get list of all available games"""
    try:
        games_index = load_games_index()
        return jsonify({
            'success': True,
            'games': games_index.get('games', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/drive-data')
def drive_data():
    """API endpoint to get drive data for a specific game"""
    try:
        opponent = request.args.get('opponent', 'Wheeling University')  # Default to Wheeling
        data = load_game_data(opponent)
        summary = get_game_summary(data, opponent)
        
        return jsonify({
            'success': True,
            'data': data,
            'summary': summary,
            'total_drives': len(data),
            'opponent': opponent
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })

@app.route('/api/plot')
def plot():
    """API endpoint to get the plot data for a specific game"""
    try:
        opponent = request.args.get('opponent', 'Wheeling University')  # Default to Wheeling
        data = load_game_data(opponent)
        fig = create_score_differential_plot(data, opponent)
        
        if fig:
            graph_json = plotly.utils.PlotlyJSONEncoder().encode(fig)
            return jsonify({
                'success': True,
                'plot': graph_json,
                'opponent': opponent
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not create plot'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
