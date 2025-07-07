#!/usr/bin/env python3
"""
Flask web application for visualizing Mercyhurst football drive data
Uses pre-scraped drive data instead of real-time scraping
"""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.utils
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def load_drive_data():
    """
    Load pre-scraped drive data from JSON file
    """
    try:
        with open('/workspaces/Mercyhurst_football_drives/drive_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Drive data file not found. Please run scrape_drive_data.py first.")
        return []
    except Exception as e:
        print(f"Error loading drive data: {e}")
        return []

def create_score_differential_plot(drive_data):
    """
    Create a Plotly graph showing score differential over time
    """
    if not drive_data:
        return None
    
    # Extract data for plotting
    elapsed_times = [drive['elapsed_seconds'] for drive in drive_data]
    differentials = [drive['score_differential'] for drive in drive_data]
    mercyhurst_scores = [drive['mercyhurst_score'] for drive in drive_data]
    wheeling_scores = [drive['wheeling_score'] for drive in drive_data]
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
        hovertemplate='<b>Time:</b> %{x} seconds<br>' +
                     '<b>Differential:</b> %{y}<br>' +
                     '<b>Score:</b> MU %{customdata[0]} - WU %{customdata[1]}<br>' +
                     '<b>Drive:</b> %{customdata[2]} %{customdata[3]}<extra></extra>',
        customdata=list(zip(mercyhurst_scores, wheeling_scores, teams, results))
    ))
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Mercyhurst vs Wheeling University - Score Differential Over Time<br>August 29, 2024',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#003366'}
        },
        xaxis_title='Elapsed Time (seconds)',
        yaxis_title='Score Differential (Mercyhurst - Wheeling)',
        template='plotly_white',
        hovermode='x unified',
        width=1200,
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add quarter markers
    quarter_times = [0, 900, 1800, 2700, 3600]  # 15 minutes per quarter
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

def get_game_summary(drive_data):
    """
    Generate a summary of the game from drive data
    """
    if not drive_data:
        return {}
    
    final_drive = drive_data[-1]
    
    # Count drives by team
    mercyhurst_drives = len([d for d in drive_data if d['team'] == 'Mercyhurst'])
    wheeling_drives = len([d for d in drive_data if d['team'] == 'Wheeling'])
    
    # Count scoring types
    mercyhurst_tds = len([d for d in drive_data if d['team'] == 'Mercyhurst' and d['result'] == 'Touchdown'])
    mercyhurst_fgs = len([d for d in drive_data if d['team'] == 'Mercyhurst' and d['result'] == 'Field Goal'])
    wheeling_tds = len([d for d in drive_data if d['team'] == 'Wheeling' and d['result'] == 'Touchdown'])
    wheeling_fgs = len([d for d in drive_data if d['team'] == 'Wheeling' and d['result'] == 'Field Goal'])
    
    return {
        'final_score': {
            'mercyhurst': final_drive['mercyhurst_score'],
            'wheeling': final_drive['wheeling_score']
        },
        'final_differential': final_drive['score_differential'],
        'total_drives': len(drive_data),
        'mercyhurst_drives': mercyhurst_drives,
        'wheeling_drives': wheeling_drives,
        'scoring_breakdown': {
            'mercyhurst': {'touchdowns': mercyhurst_tds, 'field_goals': mercyhurst_fgs},
            'wheeling': {'touchdowns': wheeling_tds, 'field_goals': wheeling_fgs}
        }
    }

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/drive-data')
def drive_data():
    """API endpoint to get drive data"""
    try:
        data = load_drive_data()
        summary = get_game_summary(data)
        
        return jsonify({
            'success': True,
            'data': data,
            'summary': summary,
            'total_drives': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })

@app.route('/api/plot')
def plot():
    """API endpoint to get the plot data"""
    try:
        data = load_drive_data()
        fig = create_score_differential_plot(data)
        
        if fig:
            graph_json = plotly.utils.PlotlyJSONEncoder().encode(fig)
            return jsonify({
                'success': True,
                'plot': graph_json
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
    app.run(debug=True, host='0.0.0.0', port=5000)
