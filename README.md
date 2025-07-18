# Mercyhurst Football Drive Analysis

A web application for analyzing Mercyhurst University football game drives, specifically focusing on the August 29, 2024 game against Wheeling University.

## Features

- **Score Differential Visualization**: Interactive plot showing how the score differential (Mercyhurst - Wheeling) changed throughout the game
- **Drive-by-Drive Breakdown**: Detailed table showing each scoring drive with timing and results
- **Game Statistics**: Summary cards showing final score, differential, and drive counts
- **Pre-scraped Data**: Uses static data files for fast loading and reliable performance

## How It Works

This application uses a two-step approach:

1. **Data Collection**: Run `scrape_drive_data.py` once to collect and process drive data from the official stats page
2. **Web Application**: The Flask app serves pre-processed data for fast, reliable visualization

## Setup and Installation

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate the drive data (run this once):
   ```bash
   python scrape_drive_data.py
   ```

3. Start the web application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Data Source

The application attempts to scrape drive data from the official Mercyhurst Athletics boxscore page:
https://hurstathletics.com/sports/football/stats/2024/wheeling-university/boxscore/14044

If live scraping is not possible (due to website structure changes or network issues), the application falls back to realistic sample data based on typical college football scoring patterns.

## Files

- `app.py`: Flask web application server
- `scrape_drive_data.py`: Data collection and processing script
- `templates/index.html`: Web interface template
- `drive_data.json`: Pre-processed drive data (generated by scraper)
- `requirements.txt`: Python package dependencies

## Game Analysis

The visualization shows:
- **X-axis**: Elapsed time in seconds from the start of the game
- **Y-axis**: Score differential (Mercyhurst score - Wheeling score)
- **Positive values**: Mercyhurst leading
- **Negative values**: Wheeling leading
- **Zero line**: Tied game

Quarter markers are shown as vertical lines to help track game progression.

## Technical Details

- **Backend**: Flask (Python web framework)
- **Visualization**: Plotly.js for interactive charts
- **Data Processing**: BeautifulSoup for HTML parsing, Pandas for data manipulation
- **Styling**: Custom CSS with Mercyhurst University colors

## Future Enhancements

- Real-time data integration
- Multiple game comparison
- Advanced statistics (yards per drive, time of possession)
- Mobile-responsive design improvements
- Export functionality for data and charts
