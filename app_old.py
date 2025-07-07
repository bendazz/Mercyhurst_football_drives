from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go
import plotly.utils
import json
import pandas as pd

app = Flask(__name__)

class GameDataScraper:
    def __init__(self, url):
        self.url = url
        self.game_data = []
        self.mercyhurst_score = 0
        self.wheeling_score = 0
        
    def scrape_play_by_play(self):
        """Scrape the play-by-play data from the game URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the play-by-play section
            play_by_play_rows = soup.find_all('tr', class_='sidearm-table-row')
            
            elapsed_seconds = 0
            quarter = 1
            
            for row in play_by_play_rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    time_cell = cells[0].get_text(strip=True)
                    team_cell = cells[1].get_text(strip=True)
                    play_cell = cells[2].get_text(strip=True)
                    
                    # Parse time and calculate elapsed seconds
                    time_info = self.parse_time(time_cell, quarter)
                    if time_info:
                        elapsed_seconds, quarter = time_info
                        
                        # Check if this is a scoring play
                        score_change = self.parse_scoring_play(play_cell, team_cell)
                        if score_change:
                            mercyhurst_points, wheeling_points = score_change
                            self.mercyhurst_score += mercyhurst_points
                            self.wheeling_score += wheeling_points
                            
                            score_diff = self.mercyhurst_score - self.wheeling_score
                            
                            self.game_data.append({
                                'elapsed_seconds': elapsed_seconds,
                                'quarter': quarter,
                                'time': time_cell,
                                'mercyhurst_score': self.mercyhurst_score,
                                'wheeling_score': self.wheeling_score,
                                'score_differential': score_diff,
                                'play': play_cell
                            })
            
            return self.game_data
            
        except Exception as e:
            print(f"Error scraping data: {e}")
            return self.generate_sample_data()
    
    def parse_time(self, time_str, current_quarter):
        """Parse time string and convert to elapsed seconds"""
        try:
            # Handle quarter changes
            if 'End of' in time_str:
                if '1st' in time_str:
                    return (15 * 60, 2)  # End of 1st quarter
                elif '2nd' in time_str:
                    return (30 * 60, 3)  # End of 2nd quarter
                elif '3rd' in time_str:
                    return (45 * 60, 4)  # End of 3rd quarter
                elif '4th' in time_str:
                    return (60 * 60, 5)  # End of 4th quarter
            
            # Parse time like "14:53" or "14:53 1st"
            time_match = re.search(r'(\d+):(\d+)', time_str)
            if time_match:
                minutes = int(time_match.group(1))
                seconds = int(time_match.group(2))
                
                # Determine quarter
                if '1st' in time_str:
                    quarter = 1
                elif '2nd' in time_str:
                    quarter = 2
                elif '3rd' in time_str:
                    quarter = 3
                elif '4th' in time_str:
                    quarter = 4
                else:
                    quarter = current_quarter
                
                # Calculate elapsed seconds
                quarter_start = (quarter - 1) * 15 * 60
                time_in_quarter = (15 * 60) - (minutes * 60 + seconds)
                elapsed_seconds = quarter_start + time_in_quarter
                
                return (elapsed_seconds, quarter)
                
        except Exception as e:
            print(f"Error parsing time {time_str}: {e}")
            
        return None
    
    def parse_scoring_play(self, play_text, team):
        """Parse scoring plays and return points scored"""
        play_lower = play_text.lower()
        
        # Initialize points
        mercyhurst_points = 0
        wheeling_points = 0
        
        # Check for scoring keywords
        is_touchdown = 'touchdown' in play_lower or 'td' in play_lower
        is_field_goal = 'field goal' in play_lower or 'fg' in play_lower
        is_extra_point = 'extra point' in play_lower or 'pat' in play_lower
        is_two_point = 'two point' in play_lower or '2-pt' in play_lower
        is_safety = 'safety' in play_lower
        
        # Determine which team scored
        team_lower = team.lower()
        is_mercyhurst = 'mercyhurst' in team_lower or 'mercy' in team_lower
        is_wheeling = 'wheeling' in team_lower
        
        # Calculate points based on scoring type
        if is_touchdown:
            points = 6
        elif is_field_goal:
            points = 3
        elif is_extra_point:
            points = 1
        elif is_two_point:
            points = 2
        elif is_safety:
            points = 2
        else:
            points = 0
        
        # Assign points to correct team
        if points > 0:
            if is_mercyhurst:
                mercyhurst_points = points
            elif is_wheeling:
                wheeling_points = points
        
        return (mercyhurst_points, wheeling_points) if points > 0 else None
    
    def generate_sample_data(self):
        """Generate sample data for demonstration purposes"""
        sample_data = [
            {'elapsed_seconds': 0, 'quarter': 1, 'mercyhurst_score': 0, 'wheeling_score': 0, 'score_differential': 0, 'play': 'Game Start'},
            {'elapsed_seconds': 420, 'quarter': 1, 'mercyhurst_score': 7, 'wheeling_score': 0, 'score_differential': 7, 'play': 'Mercyhurst Touchdown'},
            {'elapsed_seconds': 1080, 'quarter': 2, 'mercyhurst_score': 7, 'wheeling_score': 7, 'score_differential': 0, 'play': 'Wheeling Touchdown'},
            {'elapsed_seconds': 1620, 'quarter': 2, 'mercyhurst_score': 10, 'wheeling_score': 7, 'score_differential': 3, 'play': 'Mercyhurst Field Goal'},
            {'elapsed_seconds': 2700, 'quarter': 3, 'mercyhurst_score': 17, 'wheeling_score': 7, 'score_differential': 10, 'play': 'Mercyhurst Touchdown'},
            {'elapsed_seconds': 3240, 'quarter': 4, 'mercyhurst_score': 17, 'wheeling_score': 14, 'score_differential': 3, 'play': 'Wheeling Touchdown'},
            {'elapsed_seconds': 3600, 'quarter': 4, 'mercyhurst_score': 17, 'wheeling_score': 14, 'score_differential': 3, 'play': 'Game End'}
        ]
        return sample_data

def create_score_plot(game_data):
    """Create a Plotly graph showing score differential over time"""
    if not game_data:
        return None
    
    # Extract data for plotting
    elapsed_seconds = [point['elapsed_seconds'] for point in game_data]
    score_differential = [point['score_differential'] for point in game_data]
    mercyhurst_scores = [point['mercyhurst_score'] for point in game_data]
    wheeling_scores = [point['wheeling_score'] for point in game_data]
    
    # Create the plot
    fig = go.Figure()
    
    # Add score differential line
    fig.add_trace(go.Scatter(
        x=elapsed_seconds,
        y=score_differential,
        mode='lines+markers',
        name='Score Differential',
        line=dict(color='blue', width=3),
        marker=dict(size=8),
        hovertemplate='<b>Time:</b> %{x} seconds<br>' +
                      '<b>Score Differential:</b> %{y}<br>' +
                      '<b>Mercyhurst:</b> %{customdata[0]}<br>' +
                      '<b>Wheeling:</b> %{customdata[1]}<extra></extra>',
        customdata=list(zip(mercyhurst_scores, wheeling_scores))
    ))
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Mercyhurst vs Wheeling University - Score Differential Over Time<br><sub>August 29, 2024</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Elapsed Time (seconds)',
        yaxis_title='Score Differential (Mercyhurst - Wheeling)',
        hovermode='x unified',
        template='plotly_white',
        height=600,
        showlegend=True
    )
    
    # Add quarter markers
    quarter_times = [0, 900, 1800, 2700, 3600]  # 0, 15, 30, 45, 60 minutes
    quarter_labels = ['Start', 'Q2', 'Q3', 'Q4', 'End']
    
    for i, (time, label) in enumerate(zip(quarter_times, quarter_labels)):
        fig.add_vline(x=time, line_dash="dot", line_color="gray", opacity=0.5)
        fig.add_annotation(
            x=time,
            y=max(score_differential) * 0.9 if score_differential else 10,
            text=label,
            showarrow=False,
            font=dict(size=10, color="gray")
        )
    
    return fig

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/game-data')
def get_game_data():
    """API endpoint to get game data"""
    url = "https://hurstathletics.com/sports/football/stats/2024/wheeling-university/boxscore/14044"
    scraper = GameDataScraper(url)
    game_data = scraper.scrape_play_by_play()
    
    return jsonify(game_data)

@app.route('/api/plot')
def get_plot():
    """API endpoint to get the plot"""
    url = "https://hurstathletics.com/sports/football/stats/2024/wheeling-university/boxscore/14044"
    scraper = GameDataScraper(url)
    game_data = scraper.scrape_play_by_play()
    
    fig = create_score_plot(game_data)
    if fig:
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    else:
        return jsonify({'error': 'Could not create plot'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
