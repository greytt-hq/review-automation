from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
from module.scraper import scrape_reviews_from_agoda
from module.sentiment_analysis import run_sentiment_analysis

app = Flask(__name__)
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-scraping', methods=['POST'])
def start_scraping():
    city = request.form['city']
    star_rating = int(request.form['star_rating'])
    
    # Get date parameters from form (they might be empty)
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    
    # Convert date strings to DD-MM-YYYY format if they exist
    formatted_start_date = None
    formatted_end_date = None
    
    if start_date:
        try:
            # Convert from YYYY-MM-DD (HTML date input) to DD-MM-YYYY
            dt = datetime.strptime(start_date, "%Y-%m-%d")
            formatted_start_date = dt.strftime("%d-%m-%Y")
        except ValueError:
            print("⚠️ Invalid start date format, ignoring date filter")
    
    if end_date:
        try:
            # Convert from YYYY-MM-DD (HTML date input) to DD-MM-YYYY
            dt = datetime.strptime(end_date, "%Y-%m-%d")
            formatted_end_date = dt.strftime("%d-%m-%Y")
        except ValueError:
            print("⚠️ Invalid end date format, ignoring date filter")
    
    # Call the scraper with date parameters
    scrape_reviews_from_agoda(
        city=city,
        star_rating=star_rating,
        start_date=formatted_start_date,
        end_date=formatted_end_date
    )
    
    return redirect(url_for('analysis_page', city=city.lower().replace(" ", "_")))

@app.route('/analysis/<city>')
def analysis_page(city):
    return render_template('analysis.html', city=city)

@app.route('/start-analysis/<city>', methods=['POST'])
def start_analysis(city):
    input_path = f"output/agoda_{city}_hotel_reviews.csv"
    output_filename = f"sentiment_{city}.csv"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    run_sentiment_analysis(input_path, output_path)
    return render_template('download.html', filename=output_filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    try:
        print("Starting Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")


