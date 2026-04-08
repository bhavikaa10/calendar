#!/usr/bin/env python3
"""
Command-line tool for extracting dates from syllabus documents.

Usage:
    python extract_dates.py <file_path> --start YYYY-MM-DD --end YYYY-MM-DD [options]

Examples:
    python extract_dates.py syllabus.pdf --start 2024-09-01 --end 2024-12-15
    python extract_dates.py syllabus.docx --start 2024-09-01 --end 2024-12-15 --break "Spring Break:2024-03-10:2024-03-17"
    python extract_dates.py syllabus.pdf --start 2024-09-01 --end 2024-12-15 --ai --api-key sk-ant-...
"""

import argparse
import sys
import os
from datetime import datetime
import json

# Import extraction functions from backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import PyPDF2
import docx
import dateparser
import re
from datetime import timedelta


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
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def parse_recurring_dates(text, semester_start, semester_end, breaks):
    """Parse recurring date patterns like 'every Tuesday' or 'all Wednesdays'"""
    events = []

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
                current_date = semester_start
                while current_date <= semester_end:
                    if current_date.weekday() == day_num:
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

    assignment_keywords = ['assignment', 'homework', 'hw', 'problem set', 'due', 'submit']
    exam_keywords = ['exam', 'test', 'quiz', 'midterm', 'final']

    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower()

        if not line.strip():
            continue

        event_type = 'other'
        if any(keyword in line_lower for keyword in assignment_keywords):
            event_type = 'assignment'
        elif any(keyword in line_lower for keyword in exam_keywords):
            event_type = 'exam'

        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s+\d{4}\b',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\b',
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, line_lower)
            for match in matches:
                date_str = match.group()

                parsed_date = dateparser.parse(
                    date_str,
                    settings={
                        'PREFER_DATES_FROM': 'future',
                        'RELATIVE_BASE': datetime.combine(semester_start, datetime.min.time())
                    }
                )

                if parsed_date and semester_start <= parsed_date.date() <= semester_end:
                    in_break = False
                    for break_period in breaks:
                        if break_period['start'] <= parsed_date.date() <= break_period['end']:
                            in_break = True
                            break

                    if not in_break:
                        title = line.strip()[:100]

                        events.append({
                            'title': title,
                            'date': parsed_date.strftime('%Y-%m-%d'),
                            'type': event_type
                        })

    recurring_events = parse_recurring_dates(text, semester_start, semester_end, breaks)
    events.extend(recurring_events)

    unique_events = []
    seen = set()
    for event in events:
        key = (event['date'], event['title'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    return sorted(unique_events, key=lambda x: x['date'])


def ai_date_extraction(text, semester_start, semester_end, breaks, api_key):
    """Use Claude API for complex date extraction"""
    try:
        import anthropic
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

        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            events = json.loads(json_match.group())
            return sorted(events, key=lambda x: x['date'])

        return []
    except Exception as e:
        print(f"⚠️  AI extraction error: {e}", file=sys.stderr)
        return []


def print_events(events, format='table'):
    """Print events in specified format"""
    if not events:
        print("\n❌ No events found!")
        return

    print(f"\n✅ Found {len(events)} events:\n")

    if format == 'table':
        # Print as table
        print(f"{'Date':<15} {'Type':<12} {'Title'}")
        print("-" * 80)
        for event in events:
            date_str = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%b %d, %Y')
            print(f"{date_str:<15} {event['type']:<12} {event['title'][:50]}")

    elif format == 'json':
        # Print as JSON
        print(json.dumps(events, indent=2))

    elif format == 'list':
        # Print as bullet list
        for event in events:
            date_str = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%b %d, %Y')
            icon = '📝' if event['type'] == 'assignment' else '📖' if event['type'] == 'exam' else '🏫' if event['type'] == 'class' else '📌'
            print(f"{icon} {date_str} - {event['title']} ({event['type']})")


def main():
    parser = argparse.ArgumentParser(
        description='Extract important dates from syllabus documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Extract dates from a PDF:
    python extract_dates.py syllabus.pdf --start 2024-09-01 --end 2024-12-15

  Add break periods:
    python extract_dates.py syllabus.pdf --start 2024-09-01 --end 2024-12-15 \\
        --break "Thanksgiving:2024-11-25:2024-11-29" \\
        --break "Winter Break:2024-12-16:2025-01-15"

  Use AI extraction:
    python extract_dates.py syllabus.pdf --start 2024-09-01 --end 2024-12-15 \\
        --ai --api-key sk-ant-your-key-here

  Output as JSON:
    python extract_dates.py syllabus.pdf --start 2024-09-01 --end 2024-12-15 --format json
        """
    )

    parser.add_argument('file', help='Path to syllabus file (PDF, DOCX, or TXT)')
    parser.add_argument('--start', required=True, help='Semester start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='Semester end date (YYYY-MM-DD)')
    parser.add_argument('--break', action='append', dest='breaks', help='Break period (Name:YYYY-MM-DD:YYYY-MM-DD)')
    parser.add_argument('--ai', action='store_true', help='Use AI extraction (requires --api-key)')
    parser.add_argument('--api-key', help='Anthropic API key for AI extraction')
    parser.add_argument('--format', choices=['table', 'json', 'list'], default='table', help='Output format')

    args = parser.parse_args()

    # Validate file exists
    if not os.path.exists(args.file):
        print(f"❌ Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Parse dates
    try:
        semester_start = datetime.strptime(args.start, '%Y-%m-%d').date()
        semester_end = datetime.strptime(args.end, '%Y-%m-%d').date()
    except ValueError as e:
        print(f"❌ Error: Invalid date format. Use YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)

    # Parse breaks
    breaks = []
    if args.breaks:
        for break_str in args.breaks:
            try:
                name, start, end = break_str.split(':')
                breaks.append({
                    'name': name,
                    'start': datetime.strptime(start, '%Y-%m-%d').date(),
                    'end': datetime.strptime(end, '%Y-%m-%d').date()
                })
            except ValueError:
                print(f"⚠️  Warning: Invalid break format: {break_str}. Use Name:YYYY-MM-DD:YYYY-MM-DD", file=sys.stderr)

    print(f"📄 Extracting dates from: {args.file}")
    print(f"📅 Semester: {semester_start} to {semester_end}")
    if breaks:
        print(f"🏖️  Breaks: {', '.join([b['name'] for b in breaks])}")

    # Extract text
    try:
        text = extract_text(args.file)
        print(f"✓ Extracted {len(text)} characters")
    except Exception as e:
        print(f"❌ Error extracting text: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract dates
    if args.ai and args.api_key:
        print("🤖 Using AI extraction...")
        events = ai_date_extraction(text, semester_start, semester_end, breaks, args.api_key)
    else:
        print("🔍 Using local extraction...")
        events = local_date_extraction(text, semester_start, semester_end, breaks)

        if args.ai and not args.api_key:
            print("⚠️  Warning: --ai specified but no --api-key provided. Using local extraction only.", file=sys.stderr)

    # Print results
    print_events(events, format=args.format)


if __name__ == '__main__':
    main()
