# Agoda Hotel Review Scraper & Analyzer

This is an automated web scraping tool designed to collect hotel reviews from Agoda.com. It uses a Flask web interface to accept user input (city, star rating, date filter), scrapes the data using Playwright, performs sentiment analysis on the reviews, and saves the results to a CSV file.

## Features

- **Web-Based UI**: Simple interface built with Flask to start the scraping process.
- **Targeted Scraping**: Filter hotels by city and star rating.
- **Dynamic Content Handling**: Uses Playwright to navigate a modern, JavaScript-heavy website.
- **Robust Data Extraction**:
    - Clicks the "Show More" button to load up to 2,500 reviews per hotel.
    - Handles pagination on the hotel search results page.
    - Optimized for speed by fetching review data in a single, efficient batch.
- **Data Export**: Saves scraped reviews and sentiment scores to a CSV file in the `output/` directory.


## Setup and Installation

Follow these steps to set up and run the project on your local machine.

### Prerequisites

- Python 3.8 or newer
- A modern web browser (like Chrome, Firefox, or Edge)
- `pip` (Python's package installer)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd automated-module
    ```

2.  **Install Python dependencies:**
    *   This command reads the `requirements.txt` file and installs all necessary libraries directly into your Python environment. Open your command prompt or terminal and run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers:**
    *   Playwright requires downloading browser binaries to operate. This is a one-time setup step.
    ```bash
    playwright install
    ```

## How to Run the Application

1.  Make sure you are in the project's root directory (`automated-module/`).

2.  Run the Flask application from your terminal:
    ```bash
    python main.py
    ```

3.  Open your web browser and navigate to the following address:
    **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

4.  Use the web form to enter a city and star rating, then click "Start Scraping" to begin the process. The terminal will show the scraper's progress in real-time.

5.  Once finished, the scraped data and analysis will be saved as a CSV file in the `output/` folder.