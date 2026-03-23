from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename
import subprocess
import tempfile
from datetime import datetime
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max for multiple files

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/api/generate-calendar', methods=['POST'])
def generate_calendar():
    try:
        # Check if PDF files are present
        if 'pdfs' not in request.files:
            return jsonify({"error": "No PDF files provided"}), 400

        pdf_files = request.files.getlist('pdfs')
        course_codes = request.form.getlist('course_codes')

        if len(pdf_files) == 0:
            return jsonify({"error": "No files selected"}), 400

        if len(pdf_files) != len(course_codes):
            return jsonify({"error": "Mismatch between number of files and course codes"}), 400

        # Validate all files
        for pdf_file in pdf_files:
            if not allowed_file(pdf_file.filename):
                return jsonify({"error": f"Only PDF files are allowed: {pdf_file.filename}"}), 400

        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        university_url = request.form.get('university_url', '')

        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date are required"}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save all uploaded files and track their info
        saved_files = []
        for idx, (pdf_file, course_code) in enumerate(zip(pdf_files, course_codes)):
            filename = secure_filename(pdf_file.filename)
            saved_filename = f"{timestamp}_{idx}_{filename}"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            pdf_file.save(pdf_path)
            saved_files.append({
                'path': pdf_path,
                'course_code': course_code.strip()
            })

        # Generate individual calendars and collect events
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'improved_calendar.py')
        all_events_html = []
        total_events = 0

        for file_info in saved_files:
            # Generate temporary HTML for this course
            temp_output = os.path.join(app.config['OUTPUT_FOLDER'], f"temp_{timestamp}_{file_info['course_code']}.html")

            cmd = [
                'python3',
                script_path,
                file_info['path'],
                '--start', start_date,
                '--end', end_date,
                '--output', temp_output,
                '--course-code', file_info['course_code']
            ]

            if university_url:
                cmd.extend(['--url', university_url])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"Error running script for {file_info['course_code']}: {result.stderr}")
                # Clean up
                for f in saved_files:
                    if os.path.exists(f['path']):
                        os.remove(f['path'])
                return jsonify({
                    "error": f"Failed to generate calendar for {file_info['course_code']}",
                    "details": result.stderr
                }), 500

            # Count events
            import re
            match = re.search(r'Found (\d+) events', result.stdout)
            if match:
                total_events += int(match.group(1))

            # Read generated HTML (we'll extract just the calendar part later)
            with open(temp_output, 'r', encoding='utf-8') as f:
                all_events_html.append({
                    'course_code': file_info['course_code'],
                    'html': f.read()
                })

            # Clean up temp file
            os.remove(temp_output)

        # Merge all calendars into one
        output_filename = f"combined_calendar_{timestamp}.html"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        merged_html = merge_calendars(all_events_html, start_date, end_date)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(merged_html)

        # Clean up uploaded files
        for file_info in saved_files:
            os.remove(file_info['path'])

        # Read the final HTML
        with open(output_path, 'r', encoding='utf-8') as f:
            calendar_html = f.read()

        return jsonify({
            "success": True,
            "total_events": total_events,
            "num_courses": len(saved_files),
            "calendar_html": calendar_html,
            "download_url": f"/api/download/{output_filename}"
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Calendar generation timed out"}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def merge_calendars(calendars_data, start_date, end_date):
    """Merge multiple course calendars into one combined view"""

    if len(calendars_data) == 1:
        return calendars_data[0]['html']

    # Extract events from each calendar HTML
    import re
    from bs4 import BeautifulSoup

    all_events_by_date = {}
    all_breaks_by_date = {}

    # Collect course codes for color mapping
    course_codes = [c['course_code'] for c in calendars_data]

    # Define colors for different courses (assignments only - exams stay red)
    course_colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#8BC34A']
    course_color_map = {code: course_colors[i % len(course_colors)] for i, code in enumerate(course_codes)}

    for calendar_data in calendars_data:
        html = calendar_data['html']
        soup = BeautifulSoup(html, 'html.parser')

        # Find all event divs and extract date from parent structure
        calendar_tables = soup.find_all('table', class_='calendar-table')

        for table in calendar_tables:
            # Get month from header
            month_header = table.find_previous('div', class_='month-header')
            if not month_header:
                continue

            month_text = month_header.text.strip()  # e.g., "September 2025"

            # Parse all cells in this month's table
            cells = table.find_all('td')
            for cell in cells:
                day_div = cell.find('div', class_='day-number')
                if not day_div:
                    continue

                day = day_div.text.strip()
                if not day:
                    continue

                # Construct date key
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(f"{day} {month_text}", "%d %B %Y")
                    date_key = date_obj.strftime('%Y-%m-%d')
                except:
                    continue

                # Store break/holiday info if cell has those classes
                if 'break' in cell.get('class', []) or 'holiday' in cell.get('class', []):
                    break_label = cell.find('div', class_='break-label')
                    holiday_label = cell.find('div', class_='holiday-label')

                    if date_key not in all_breaks_by_date:
                        all_breaks_by_date[date_key] = {
                            'classes': cell.get('class', []),
                            'label': break_label.text.strip() if break_label else (holiday_label.text.strip() if holiday_label else ''),
                            'label_class': 'break-label' if break_label else 'holiday-label'
                        }

                # Extract all events from this cell
                event_divs = cell.find_all('div', class_='event')
                for event_div in event_divs:
                    event_type = 'exam' if 'exam' in event_div.get('class', []) else 'assignment'
                    event_title = event_div.text.strip()

                    # Extract course code from event title
                    course_code_match = re.match(r'\[([A-Z]{3}\d{3})\]', event_title)
                    course_code = course_code_match.group(1) if course_code_match else None

                    if date_key not in all_events_by_date:
                        all_events_by_date[date_key] = []

                    all_events_by_date[date_key].append({
                        'title': event_title,
                        'type': event_type,
                        'course_code': course_code
                    })

    # Now generate a new combined HTML calendar
    # Use the first calendar as a template but replace events
    base_html = calendars_data[0]['html']
    soup = BeautifulSoup(base_html, 'html.parser')

    # Add custom CSS for course colors in the style tag
    style_tag = soup.find('style')
    if style_tag:
        additional_css = '\n'
        for course_code, color in course_color_map.items():
            additional_css += f'''        .event.assignment.{course_code.lower()} {{
            background: {color};
        }}
'''
        # Insert before the closing style tag
        style_tag.string = style_tag.string + additional_css

    # Update title
    title_tag = soup.find('h1')
    if title_tag:
        title_tag.string = 'Course Calendar'

    # Update HTML page title
    page_title = soup.find('title')
    if page_title:
        page_title.string = 'Course Calendar'

    # Keep semester info as is, don't mention course codes
    semester_info = soup.find('div', class_='semester-info')
    if semester_info:
        # Keep existing semester dates without course codes
        existing_text = semester_info.text.strip()
        if 'Semester:' in existing_text:
            semester_info.string = existing_text

    # Update all calendar cells with merged events
    calendar_tables = soup.find_all('table', class_='calendar-table')

    for table in calendar_tables:
        month_header = table.find_previous('div', class_='month-header')
        if not month_header:
            continue

        month_text = month_header.text.strip()

        cells = table.find_all('td')
        for cell in cells:
            day_div = cell.find('div', class_='day-number')
            if not day_div:
                continue

            day = day_div.text.strip()
            if not day:
                continue

            try:
                from datetime import datetime
                date_obj = datetime.strptime(f"{day} {month_text}", "%d %B %Y")
                date_key = date_obj.strftime('%Y-%m-%d')
            except:
                continue

            # Apply break/holiday styling if exists
            if date_key in all_breaks_by_date:
                break_info = all_breaks_by_date[date_key]
                cell['class'] = break_info['classes']

                # Add break/holiday label if not already present
                existing_label = cell.find('div', class_=break_info['label_class'])
                if not existing_label and break_info['label']:
                    label_div = soup.new_tag('div', **{'class': break_info['label_class']})
                    label_div.string = break_info['label']
                    # Insert after day-number
                    if day_div:
                        day_div.insert_after(label_div)

            # Remove existing event divs only
            for event_div in cell.find_all('div', class_='event'):
                event_div.decompose()

            # Add merged events for this date
            if date_key in all_events_by_date:
                for event in all_events_by_date[date_key]:
                    # Build class list
                    event_classes = ['event', event['type']]
                    if event['course_code'] and event['type'] == 'assignment':
                        event_classes.append(event['course_code'].lower())

                    new_event = soup.new_tag('div', **{'class': ' '.join(event_classes)})
                    new_event.string = event['title']
                    cell.append(new_event)

    return str(soup)

@app.route('/api/download/<filename>', methods=['GET'])
def download_calendar(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/html'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
