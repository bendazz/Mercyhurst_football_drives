# Mercyhurst Football Score Analysis

A web application that analyzes the score differential over time for Mercyhurst University football games, specifically focusing on the game against Wheeling University on August 29, 2024.

## Features

- **Interactive Score Visualization**: Plot showing score differential (Mercyhurst - Wheeling) over elapsed game time
- **Real-time Data Scraping**: Attempts to scrape live data from the official game statistics
- **Responsive Design**: Modern, mobile-friendly web interface
- **Game Statistics**: Display of final scores, scoring plays, and game progression
- **Fallback Sample Data**: Demonstrates functionality even when live data is unavailable

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your web browser and navigate to `http://localhost:5000`

## Usage

The application automatically loads when you visit the homepage. It will:

1. Attempt to scrape play-by-play data from the official game page
2. Parse scoring events and calculate elapsed time
3. Create an interactive plot showing the score differential over time
4. Display game statistics and final scores

## Technical Details

- **Backend**: Flask (Python web framework)
- **Data Scraping**: Beautiful Soup + Requests
- **Visualization**: Plotly.js for interactive charts
- **Frontend**: Bootstrap 5 for responsive design
- **Data Processing**: Pandas for data manipulation

## Game Information

- **Teams**: Mercyhurst University Lakers vs Wheeling University Cardinals
- **Date**: August 29, 2024
- **Source**: https://hurstathletics.com/sports/football/stats/2024/wheeling-university/boxscore/14044

## Plot Interpretation

- **X-axis**: Elapsed time in seconds from game start
- **Y-axis**: Score differential (Mercyhurst score - Wheeling score)
- **Positive values**: Mercyhurst is leading
- **Negative values**: Wheeling is leading
- **Zero line**: Game is tied
- **Quarter markers**: Vertical lines showing quarter boundaries

## Testing

Run the test script to verify web scraping functionality:
```bash
python test_scraping.py
```

## Note

The application includes fallback sample data for demonstration purposes if the live website data cannot be accessed due to network issues or website structure changes.