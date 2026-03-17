from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import dateparser
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import anthropic

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text(file_path):
    """Extract text based on file extension"""
    extension = file_path.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        return extract_text_from_txt(file_path)
    return ""

def parse_recurring_dates(text, semester_start, semester_end, breaks):
    """Parse recurring date patterns like 'every Tuesday' or 'all Wednesdays'"""
    events = []

    # Pattern for "every [day]" or "all [days]"
    day_patterns = [
        r'(?:every|all|each)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?',
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?\s+(?:class|classes|lecture|lectures)'
    ]

    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }

    for pattern in day_patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            day_name = match.group(1)
            day_num = days_map.get(day_name)

            if day_num is not None:
                # Generate dates for this day of week
                current_date = semester_start
                while current_date <= semester_end:
                    if current_date.weekday() == day_num:
                        # Check if date falls in a break period
                        in_break = False
                        for break_period in breaks:
                            if break_period['start'] <= current_date <= break_period['end']:
                                in_break = True
                                break

                        if not in_break:
                            events.append({
                                'title': f'Class - {day_name.capitalize()}',
                                'date': current_date.strftime('%Y-%m-%d'),
                                'type': 'class'
                            })
                    current_date += timedelta(days=1)

    return events

def local_date_extraction(text, semester_start, semester_end, breaks):
    """Extract dates using local NLP libraries and regex patterns"""
    events = []

    # Keywords to identify event types
    assignment_keywords = ['assignment', 'homework', 'hw', 'problem set', 'due', 'submit']
    exam_keywords = ['exam', 'test', 'quiz', 'midterm', 'final']

    # Split text into lines for better context
    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower()

        # Skip empty lines
        if not line.strip():
            continue

        # Determine event type
        event_type = 'other'
        if any(keyword in line_lower for keyword in assignment_keywords):
            event_type = 'assignment'
        elif any(keyword in line_lower for keyword in exam_keywords):
            event_type = 'exam'

        # Try to parse dates from the line
        # Common date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or M/D/YY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s+\d{4}\b',  # DD Month YYYY
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\b',  # Month DD
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, line_lower)
            for match in matches:
                date_str = match.group()

                # Parse the date
                parsed_date = dateparser.parse(
                    date_str,
                    settings={
                        'PREFER_DATES_FROM': 'future',
                        'RELATIVE_BASE': semester_start
                    }
                )

                if parsed_date and semester_start <= parsed_date.date() <= semester_end:
                    # Check if in break period
                    in_break = False
                    for break_period in breaks:
                        if break_period['start'] <= parsed_date.date() <= break_period['end']:
                            in_break = True
                            break

                    if not in_break:
                        # Extract title (try to get context from line)
                        title = line.strip()[:100]  # Limit title length

                        events.append({
                            'title': title,
                            'date': parsed_date.strftime('%Y-%m-%d'),
                            'type': event_type
                        })

    # Also try to find recurring dates
    recurring_events = parse_recurring_dates(text, semester_start, semester_end, breaks)
    events.extend(recurring_events)

    # Remove duplicates
    unique_events = []
    seen = set()
    for event in events:
        key = (event['date'], event['title'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    return unique_events

def ai_date_extraction(text, semester_start, semester_end, breaks, api_key):
    """Use Claude API as fallback for complex date extraction"""
    try:
        client = anthropic.Anthropic(api_key=api_key)

        breaks_text = "\n".join([f"- {b['name']}: {b['start']} to {b['end']}" for b in breaks])

        prompt = f"""Extract all important academic dates from the following syllabus text.

Semester Information:
- Start Date: {semester_start}
- End Date: {semester_end}
- Breaks:
{breaks_text}

Please identify:
1. Assignment due dates
2. Exam dates (quizzes, midterms, finals)
3. Class meeting dates (if they mention specific patterns like "every Tuesday")
4. Project deadlines
5. Any other important academic dates

For recurring events like "every Tuesday", generate individual dates for each occurrence during the semester (excluding break periods).

Return the results as a JSON array with this format:
[
  {{"title": "Assignment 1 Due", "date": "YYYY-MM-DD", "type": "assignment"}},
  {{"title": "Midterm Exam", "date": "YYYY-MM-DD", "type": "exam"}},
  {{"title": "Class Meeting", "date": "YYYY-MM-DD", "type": "class"}}
]

Syllabus Text:
{text[:5000]}

Return ONLY the JSON array, no other text."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        import json
        # Try to find JSON array in response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            events = json.loads(json_match.group())
            return events

        return []
    except Exception as e:
        print(f"AI extraction error: {e}")
        return []

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and date extraction"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Get semester information
    semester_start_str = request.form.get('semester_start')
    semester_end_str = request.form.get('semester_end')
    breaks_str = request.form.get('breaks', '[]')

    if not semester_start_str or not semester_end_str:
        return jsonify({'error': 'Semester start and end dates required'}), 400

    try:
        semester_start = datetime.strptime(semester_start_str, '%Y-%m-%d').date()
        semester_end = datetime.strptime(semester_end_str, '%Y-%m-%d').date()

        import json
        breaks = json.loads(breaks_str)
        # Convert break dates to date objects
        for break_period in breaks:
            break_period['start'] = datetime.strptime(break_period['start'], '%Y-%m-%d').date()
            break_period['end'] = datetime.strptime(break_period['end'], '%Y-%m-%d').date()

    except Exception as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400

    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Extract text from document
        text = extract_text(filepath)

        # Try local extraction first
        events = local_date_extraction(text, semester_start, semester_end, breaks)

        # If local extraction found very few events, try AI extraction
        use_ai = request.form.get('use_ai', 'false').lower() == 'true'
        api_key = request.form.get('api_key', '')

        if use_ai and api_key and len(events) < 3:
            ai_events = ai_date_extraction(text, semester_start, semester_end, breaks, api_key)
            if ai_events:
                events = ai_events

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'events': events,
            'extraction_method': 'ai' if use_ai and len(events) >= 3 else 'local'
        })

    except Exception as e:
        # Clean up file on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_url():
    """Scrape dates from a school calendar URL"""
    data = request.json
    url = data.get('url')
    semester_start_str = data.get('semester_start')
    semester_end_str = data.get('semester_end')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    try:
        import requests
        from bs4 import BeautifulSoup

        semester_start = datetime.strptime(semester_start_str, '%Y-%m-%d').date()
        semester_end = datetime.strptime(semester_end_str, '%Y-%m-%d').date()

        # Fetch the webpage
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Use local extraction on scraped text
        events = local_date_extraction(text, semester_start, semester_end, [])

        return jsonify({
            'success': True,
            'events': events
        })

    except Exception as e:
        return jsonify({'error': f'Scraping error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
