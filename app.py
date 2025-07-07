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
    
    # Extract data for plotting and ensure proper sorting, filtering out problematic entries
    plot_data = []
    for drive in drive_data:
        # Skip entries that are not valid drives (Game Start, Game End, or incomplete entries)
        if (drive['team'] in ['Game Start', 'Game End'] or 
            drive['result'] in ['Game Start', 'Game End'] or
            not drive.get('play_description', '').strip()):
            continue
            
        plot_data.append((
            drive['elapsed_seconds'] / 60,  # Convert to minutes
            drive['score_differential'], 
            drive['mercyhurst_score'], 
            drive['opponent_score'], 
            drive['team'], 
            drive['result']
        ))
    
    # Sort by elapsed time to ensure proper ordering
    plot_data.sort(key=lambda x: x[0])
    
    # Add game start point (0,0) and game end point (60, final differential)
    if plot_data:
        final_differential = plot_data[-1][1]  # Get the final score differential
        final_merc_score = plot_data[-1][2]
        final_opp_score = plot_data[-1][3]
        
        # Insert game start point at the beginning
        plot_data.insert(0, (0, 0, 0, 0, 'Game Start', 'Game Start'))
        
        # Add game end point at the end
        plot_data.append((60, final_differential, final_merc_score, final_opp_score, 'Game End', 'Game End'))
    
    elapsed_times = [item[0] for item in plot_data]
    differentials = [item[1] for item in plot_data]
    mercyhurst_scores = [item[2] for item in plot_data]
    opponent_scores = [item[3] for item in plot_data]
    teams = [item[4] for item in plot_data]
    results = [item[5] for item in plot_data]
    
    # Create the plot
    fig = go.Figure()
    
    # Add the main line with explicit control
    fig.add_trace(go.Scatter(
        x=elapsed_times,
        y=differentials,
        mode='lines+markers',
        name='Score Differential',
        line=dict(color='#003366', width=3, shape='linear'),  # Mercyhurst blue
        marker=dict(size=8, color='#003366'),
        fill=None,
        connectgaps=False,
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

def create_comparison_plots(games_data):
    """
    Create smaller plots for all games to display in a comparison view
    """
    from plotly.subplots import make_subplots
    
    if not games_data:
        return None
    
    # Calculate grid dimensions
    num_games = len(games_data)
    cols = 3  # 3 columns
    rows = (num_games + cols - 1) // cols  # Calculate rows needed
    
    # Create subplots
    fig = make_subplots(
        rows=rows, 
        cols=cols,
        subplot_titles=[f"vs {game['opponent']}" for game in games_data],
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )
    
    for i, game_data in enumerate(games_data):
        row = i // cols + 1
        col = i % cols + 1
        
        opponent_name = game_data['opponent']
        drive_data = game_data['data']
        
        if not drive_data:
            continue
            
        # Extract and filter data (same logic as main plot)
        plot_data = []
        for drive in drive_data:
            if (drive['team'] in ['Game Start', 'Game End'] or 
                drive['result'] in ['Game Start', 'Game End'] or
                not drive.get('play_description', '').strip()):
                continue
                
            plot_data.append((
                drive['elapsed_seconds'] / 60,
                drive['score_differential'], 
                drive['mercyhurst_score'], 
                drive['opponent_score'], 
                drive['team'], 
                drive['result']
            ))
        
        if not plot_data:
            continue
            
        # Sort by elapsed time
        plot_data.sort(key=lambda x: x[0])
        
        # Add game start and end points
        final_differential = plot_data[-1][1]
        final_merc_score = plot_data[-1][2]
        final_opp_score = plot_data[-1][3]
        
        plot_data.insert(0, (0, 0, 0, 0, 'Game Start', 'Game Start'))
        plot_data.append((60, final_differential, final_merc_score, final_opp_score, 'Game End', 'Game End'))
        
        elapsed_times = [item[0] for item in plot_data]
        differentials = [item[1] for item in plot_data]
        mercyhurst_scores = [item[2] for item in plot_data]
        opponent_scores = [item[3] for item in plot_data]
        
        # Add trace to subplot
        fig.add_trace(
            go.Scatter(
                x=elapsed_times,
                y=differentials,
                mode='lines+markers',
                name=f'vs {opponent_name}',
                line=dict(color='#003366', width=2),
                marker=dict(size=4, color='#003366'),
                showlegend=False,
                hovertemplate=f'<b>{opponent_name}</b><br>' +
                             '<b>Time:</b> %{x:.1f} min<br>' +
                             '<b>Differential:</b> %{y}<br>' +
                             f'<b>Score:</b> MU %{{customdata[0]}} - %{{customdata[1]}}<extra></extra>',
                customdata=list(zip(mercyhurst_scores, opponent_scores))
            ),
            row=row, col=col
        )
        
        # Add horizontal line at y=0 for each subplot
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3, row=row, col=col)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Mercyhurst Football 2024 Season - All Games Comparison<br>Score Differential Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#003366'}
        },
        template='plotly_white',
        height=300 * rows,  # Adjust height based on number of rows
        width=1400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Update x and y axes for all subplots
    for i in range(1, rows * cols + 1):
        fig.update_xaxes(title_text="Time (min)", range=[0, 60], row=(i-1)//cols + 1, col=(i-1)%cols + 1)
        fig.update_yaxes(title_text="Score Diff", row=(i-1)//cols + 1, col=(i-1)%cols + 1)
    
    return fig

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

@app.route('/api/comparison-plot')
def comparison_plot():
    """API endpoint to get comparison plots for all games"""
    try:
        games_index = load_games_index()
        games_list = games_index.get('games', [])
        
        if not games_list:
            return jsonify({
                'success': False,
                'error': 'No games found'
            })
        
        # Load data for all games
        games_data = []
        for game in games_list:
            opponent_name = game['opponent']
            data = load_game_data(opponent_name)
            if data:  # Only include games with data
                games_data.append({
                    'opponent': opponent_name,
                    'data': data
                })
        
        if not games_data:
            return jsonify({
                'success': False,
                'error': 'No game data found'
            })
        
        fig = create_comparison_plots(games_data)
        
        if fig:
            graph_json = plotly.utils.PlotlyJSONEncoder().encode(fig)
            return jsonify({
                'success': True,
                'plot': graph_json,
                'games_count': len(games_data)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not create comparison plot'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
