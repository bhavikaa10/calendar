#!/usr/bin/env python3
"""
Improved calendar generator with all assignments and better break display
"""

import PyPDF2
import re
from datetime import datetime, timedelta
import calendar as cal
import sys
import requests
from bs4 import BeautifulSoup

# Set calendar to start on Sunday (US style)
cal.setfirstweekday(cal.SUNDAY)

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def scrape_university_calendar(url):
    """Scrape dates from university calendar URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        print(f"✓ Scraped {len(text)} characters from URL")
        return text
    except Exception as e:
        print(f"⚠️  Warning: Could not scrape URL: {e}")
        return ""

def extract_breaks_and_holidays(text, semester_start, semester_end):
    """Extract break periods and holidays - deduplicated with overlap merging"""
    breaks_list = []

    month_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
        'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
        'may': 5, 'jun': 6, 'june': 6,
        'jul': 7, 'july': 7, 'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }

    # Pattern for date ranges "Oct 27-31" or "Oct. 27 - Oct. 31"
    range_pattern = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})\s*[-–]\s*(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+)?(\d{1,2})'

    for match in re.finditer(range_pattern, text.lower()):
        groups = match.groups()
        month_str = groups[0]
        start_day = groups[1]
        end_month = groups[2] if groups[2] else groups[0]  # Use same month if not specified
        end_day = groups[3]

        # Get context - check same line (up to 60 chars after the date)
        context_start = max(0, match.start() - 5)
        context_end = min(len(text), match.end() + 60)
        context = text[context_start:context_end].lower()

        # Check for break keywords on the same line
        # Use strict patterns to avoid false positives
        if 'reading break' in context or 'reading week' in context:
            # Skip if it says "Fall 2025" or "Fall 2026" (semester labels, not breaks)
            if 'fall 2025' in context or 'fall 2026' in context:
                continue
        elif 'fall break' in context or 'spring break' in context or 'winter break' in context:
            pass
        else:
            # Not a break
            continue

        month_num = month_map[month_str]

        for year in [semester_start.year, semester_end.year]:
            try:
                start_date = datetime(year, month_num, int(start_day)).date()
                end_date = datetime(year, month_num, int(end_day)).date()

                if semester_start <= start_date <= semester_end:
                    # Determine break name
                    if 'reading' in context:
                        name = "Reading Week"
                    elif 'spring' in context:
                        name = "Spring Break"
                    elif 'fall' in context:
                        name = "Fall Break"
                    else:
                        name = "Break"

                    breaks_list.append({
                        'name': name,
                        'start': start_date,
                        'end': end_date,
                        'type': 'break'
                    })
                    break
            except ValueError:
                continue

    # Merge overlapping breaks
    if not breaks_list:
        return []

    # Sort by start date
    breaks_list.sort(key=lambda x: x['start'])

    merged = [breaks_list[0]]
    for current in breaks_list[1:]:
        last = merged[-1]
        # Check if overlapping or adjacent (within 3 days)
        if current['start'] <= last['end'] + timedelta(days=3):
            # Merge - extend the end date if needed
            if current['end'] > last['end']:
                last['end'] = current['end']
        else:
            merged.append(current)

    breaks_dict = {}

    # Pattern for single-day holidays "Monday, October 13"
    single_day_pattern = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})'

    for match in re.finditer(single_day_pattern, text, re.IGNORECASE):
        day_name, month_str, day = match.groups()

        context_start = max(0, match.start() - 80)
        context_end = min(len(text), match.end() + 80)
        context = text[context_start:context_end].lower()

        # Check for holiday keywords
        if any(keyword in context for keyword in ['thanksgiving', 'holiday', 'closed']):
            month_num = month_map[month_str.lower()]

            for year in [semester_start.year, semester_end.year]:
                try:
                    holiday_date = datetime(year, month_num, int(day)).date()

                    if semester_start <= holiday_date <= semester_end:
                        if 'thanksgiving' in context:
                            name = "Thanksgiving"
                        else:
                            name = "Holiday"

                        merged.append({
                            'name': name,
                            'start': holiday_date,
                            'end': holiday_date,
                            'type': 'holiday'
                        })
                        break
                except ValueError:
                    continue

    return merged

def is_date_in_break(date, breaks):
    """Check if a date falls within any break period"""
    for break_period in breaks:
        if break_period['start'] <= date <= break_period['end']:
            return break_period
    return None

def extract_all_events(text, semester_start, semester_end, breaks):
    """Extract ALL events including quizzes, reflections, worksheets"""
    events = []
    text_lower = text.lower()

    month_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
        'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
        'may': 5, 'jun': 6, 'june': 6,
        'jul': 7, 'july': 7, 'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }

    # 1. Extract exam and quiz dates using flexible pattern matching
    # Pattern handles: "Monday, Oct 6, 2025" or "Thursday, Oct. 16" or "Mon, Oct 20, 2025"
    exam_pattern = r'(mon|monday|tue|tuesday|wed|wednesday|thu|thursday|fri|friday|sat|saturday|sun|sunday),?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|september|oct|october|nov|november|dec|december)[a-z]*\.?\s+(\d{1,2})'

    for match in re.finditer(exam_pattern, text, re.IGNORECASE):
        day_name, month_str, day = match.groups()

        # Get VERY TIGHT context - just before the date (same line)
        # This prevents picking up keywords from other rows in tables
        context_start = max(0, match.start() - 40)
        context_end = min(len(text), match.end() + 20)
        context = text[context_start:context_end].lower()

        # Skip breaks and non-academic dates
        if any(keyword in context for keyword in ['reading week', 'reading break', 'fall break', 'spring break', 'no class']):
            continue

        event_title = None
        event_type = None

        # Priority 1: Skip final exam mentions
        if 'final exam' in context or 'exam period' in context:
            continue

        # Priority 2: Check for exams/tests (highest priority)
        if 'term test' in context:
            if 'makeup' in context or 'make-up' in context:
                event_title = 'Makeup Term Test'
                event_type = 'exam'
            elif 'earlier' in context:
                event_title = 'Term Test (Earlier Sitting)'
                event_type = 'exam'
            elif 'main' in context or 'default' in context or 'exam center' in context:
                event_title = 'Term Test'
                event_type = 'exam'
            else:
                event_title = 'Term Test'
                event_type = 'exam'
        elif 'midterm' in context or 'mid-term' in context:
            if 'makeup' in context:
                event_title = 'Makeup Midterm'
                event_type = 'exam'
            else:
                event_title = 'Midterm'
                event_type = 'exam'
        # Priority 3: Check for prerequisite/syllabus quiz
        elif any(keyword in context for keyword in ['prerequisite', 'pre-requisite', 'syllabus quiz']):
            event_title = 'Pre-requisite & Syllabus Quiz'
            event_type = 'assignment'
        # Priority 4: Check for numbered assignments
        elif re.search(r'\bassignment\s+(\d+)', context, re.IGNORECASE):
            assignment_match = re.search(r'\bassignment\s+(\d+)', context, re.IGNORECASE)
            assignment_num = assignment_match.group(1)
            event_title = f'Assignment {assignment_num} Due'
            event_type = 'assignment'
        # Priority 5: Check for surveys
        elif re.search(r'\bsurvey\s+(\d+)', context, re.IGNORECASE):
            survey_match = re.search(r'\bsurvey\s+(\d+)', context, re.IGNORECASE)
            survey_num = survey_match.group(1)
            event_title = f'Survey {survey_num}'
            event_type = 'assignment'
        # Priority 6: Check for quizzes (not weekly)
        elif 'quiz' in context and 'weekly' not in context and 'every' not in context:
            quiz_match = re.search(r'quiz\s+(\d+)', context, re.IGNORECASE)
            if quiz_match:
                quiz_num = quiz_match.group(1)
                event_title = f'Quiz {quiz_num}'
                event_type = 'assignment'
        # If no match, skip
        else:
            continue

        if event_title and event_type:
            month_num = month_map[month_str.lower()[:3]]

            for year in [semester_start.year, semester_end.year]:
                try:
                    event_date = datetime(year, month_num, int(day)).date()

                    if semester_start <= event_date <= semester_end:
                        if not is_date_in_break(event_date, breaks):
                            events.append({
                                'title': event_title,
                                'date': event_date,
                                'type': event_type
                            })
                        break
                except (ValueError, KeyError):
                    continue

    # 2. Extract project dates
    date_patterns = [
        r'(thursday|friday|monday|tuesday|wednesday|saturday|sunday),?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})',
    ]

    for pattern in date_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            groups = match.groups()
            day_name, month_str, day = groups

            # Get context
            context_start = max(0, match.start() - 100)
            context_end = min(len(text), match.end() + 100)
            context = text[context_start:context_end]

            # Skip if it's a break, exam, or quiz
            skip_keywords = ['reading week', 'break', 'recess', 'term test', 'final exam', 'prerequisite', 'syllabus quiz']
            if any(keyword in context.lower() for keyword in skip_keywords):
                continue

            # Only extract project parts
            if 'part 0' in context.lower() and 'team' in context.lower():
                event_title = 'Project Part 0: Team Agreement'
                event_type = 'assignment'
            elif 'part 1' in context.lower() and ('proposal' in context.lower() or 'research' in context.lower()):
                event_title = 'Project Part 1: Proposal'
                event_type = 'assignment'
            elif 'part 2' in context.lower() or ('poster' in context.lower() and 'presentation' in context.lower()):
                event_title = 'Project Part 2: Poster & Presentation'
                event_type = 'assignment'
            elif 'part 3' in context.lower() and 'reflection' in context.lower():
                event_title = 'Project Part 3: Group Work Reflection'
                event_type = 'assignment'
            else:
                continue

            month_num = month_map[month_str.lower()]

            for year in [semester_start.year, semester_end.year]:
                try:
                    event_date = datetime(year, month_num, int(day)).date()

                    if semester_start <= event_date <= semester_end:
                        if not is_date_in_break(event_date, breaks):
                            events.append({
                                'title': event_title,
                                'date': event_date,
                                'type': event_type
                            })
                        break
                except ValueError:
                    continue

    # 2. Detect weekly recurring assignments
    day_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }

    # Look for weekly quizzes
    for day_name, day_num in day_map.items():
        if f'quiz' in text_lower and day_name in text_lower:
            # Check if it's described as weekly/every week
            if 'every' in text_lower or 'weekly' in text_lower or f'{day_name}s' in text_lower:
                current = semester_start
                while current <= semester_end:
                    if current.weekday() == day_num:
                        if not is_date_in_break(current, breaks):
                            events.append({
                                'title': 'Weekly Quiz Due (11:59 PM)',
                                'date': current,
                                'type': 'assignment'
                            })
                    current += timedelta(days=1)
                break  # Only generate for one day

    # Look for weekly reflections
    for day_name, day_num in day_map.items():
        if 'reflection' in text_lower and day_name in text_lower:
            if 'every' in text_lower or 'weekly' in text_lower or f'{day_name}s' in text_lower:
                current = semester_start
                while current <= semester_end:
                    if current.weekday() == day_num:
                        if not is_date_in_break(current, breaks):
                            events.append({
                                'title': 'Weekly Reflection Due (11:59 PM)',
                                'date': current,
                                'type': 'assignment'
                            })
                    current += timedelta(days=1)
                break

    # Look for weekly worksheets
    for day_name, day_num in day_map.items():
        if 'worksheet' in text_lower and day_name in text_lower:
            if 'every' in text_lower or 'weekly' in text_lower or f'{day_name}s' in text_lower:
                current = semester_start
                while current <= semester_end:
                    if current.weekday() == day_num:
                        if not is_date_in_break(current, breaks):
                            events.append({
                                'title': 'MarkUs Worksheet Due (11:59 PM)',
                                'date': current,
                                'type': 'assignment'
                            })
                    current += timedelta(days=1)
                break

    # Deduplicate events (same title and date)
    seen = set()
    unique_events = []
    for event in events:
        key = (event['title'], event['date'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    return sorted(unique_events, key=lambda x: x['date'])

def generate_html_calendar(events, breaks, semester_start, semester_end, output_file):
    """Generate HTML calendar with events and highlighted break dates"""

    # Group events by date
    events_by_date = {}
    for event in events:
        date_str = event['date'].strftime('%Y-%m-%d')
        if date_str not in events_by_date:
            events_by_date[date_str] = []
        events_by_date[date_str].append(event)

    # Format values first
    semester_start_str = semester_start.strftime('%B %d, %Y')
    semester_end_str = semester_end.strftime('%B %d, %Y')

    # HTML start
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Course Calendar</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }}
        .semester-info {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .month-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            margin: 30px 0 15px 0;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
        }}
        .calendar-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        .calendar-table th {{
            background: #f0f0f0;
            padding: 10px;
            border: 1px solid #ddd;
            font-weight: 600;
        }}
        .calendar-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            vertical-align: top;
            height: 100px;
            width: 14.28%;
            position: relative;
        }}
        .calendar-table td.empty {{
            background: #fafafa;
        }}
        .calendar-table td.break {{
            background: #ffe6e6;
        }}
        .calendar-table td.holiday {{
            background: #fff3cd;
        }}
        .day-number {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .break-label {{
            font-size: 9px;
            color: #dc3545;
            font-weight: bold;
            margin-top: 2px;
        }}
        .holiday-label {{
            font-size: 9px;
            color: #856404;
            font-weight: bold;
            margin-top: 2px;
        }}
        .event {{
            background: #4CAF50;
            color: white;
            padding: 4px 6px;
            margin: 3px 0;
            border-radius: 4px;
            font-size: 11px;
            line-height: 1.3;
            word-wrap: break-word;
        }}
        .event.exam {{
            background: #f44336;
        }}
        .event.assignment {{
            background: #2196F3;
        }}
        .summary {{
            margin-top: 40px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        .summary h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .summary-item {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .summary-date {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>Course Calendar</h1>
    <div class="semester-info">
        Semester: {semester_start_str} to {semester_end_str}
    </div>
"""

    # Generate calendar months
    current_date = semester_start.replace(day=1)
    end_month = semester_end.replace(day=1)

    while current_date <= end_month:
        month_name = current_date.strftime('%B %Y')
        html += f'<div class="month-header">{month_name}</div>'
        html += '<table class="calendar-table"><thead><tr>'
        html += '<th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th>'
        html += '</tr></thead><tbody>'

        # Get calendar for this month
        month_cal = cal.monthcalendar(current_date.year, current_date.month)

        for week in month_cal:
            html += '<tr>'
            for day in week:
                if day == 0:
                    html += '<td class="empty"></td>'
                else:
                    date_obj = datetime(current_date.year, current_date.month, day).date()
                    date_str = date_obj.strftime('%Y-%m-%d')

                    # Check if this date is in a break
                    break_info = is_date_in_break(date_obj, breaks)

                    if break_info:
                        if break_info['type'] == 'holiday':
                            html += '<td class="holiday">'
                        else:
                            html += '<td class="break">'
                    else:
                        html += '<td>'

                    html += f'<div class="day-number">{day}</div>'

                    # Add break/holiday label
                    if break_info:
                        if break_info['type'] == 'holiday':
                            html += f'<div class="holiday-label">{break_info["name"]}</div>'
                        else:
                            html += f'<div class="break-label">{break_info["name"]}</div>'

                    # Add events
                    if date_str in events_by_date:
                        for event in events_by_date[date_str]:
                            html += f'<div class="event {event["type"]}">{event["title"]}</div>'

                    html += '</td>'
            html += '</tr>'

        html += '</tbody></table>'

        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    html += '</div></body></html>'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n📝 Generating calendar: {output_file}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Extract dates from syllabus and create calendar')
    parser.add_argument('pdf_file', help='Path to the syllabus PDF file')
    parser.add_argument('--start', required=True, help='Semester start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='Semester end date (YYYY-MM-DD)')
    parser.add_argument('--url', help='University calendar URL to scrape for breaks')
    parser.add_argument('--output', default='calendar.html', help='Output HTML file')
    parser.add_argument('--course-code', help='Course code to prefix events (e.g., STA302)')

    args = parser.parse_args()
    course_code = args.course_code if hasattr(args, 'course_code') and args.course_code else None

    # Parse dates
    semester_start = datetime.strptime(args.start, '%Y-%m-%d').date()
    semester_end = datetime.strptime(args.end, '%Y-%m-%d').date()

    print(f"📄 Reading syllabus: {args.pdf_file}")
    text = extract_text_from_pdf(args.pdf_file)

    # Scrape university calendar if URL provided (but don't use it for breaks - only use syllabus)
    # The university calendar may have different break dates than the course syllabus
    # if args.url:
    #     print(f"🌐 Scraping university calendar: {args.url}")
    #     uni_text = scrape_university_calendar(args.url)
    #     text += "\n" + uni_text

    print(f"📅 Semester: {semester_start} to {semester_end} (last day of classes)")

    # Extract breaks
    print("🔍 Extracting breaks and holidays...")
    breaks = extract_breaks_and_holidays(text, semester_start, semester_end)

    if breaks:
        print(f"✓ Found {len(breaks)} break periods/holidays:")
        for break_period in breaks:
            if break_period['type'] == 'holiday':
                print(f"   🎉 {break_period['name']}: {break_period['start'].strftime('%b %d, %Y')}")
            else:
                print(f"   🏖️  {break_period['name']}: {break_period['start'].strftime('%b %d')} - {break_period['end'].strftime('%b %d, %Y')}")

    # Extract events
    print("\n🔍 Extracting events (excluding breaks)...")
    events = extract_all_events(text, semester_start, semester_end, breaks)

    # Add course code prefix to all event titles if provided
    if course_code:
        for event in events:
            event['title'] = f"[{course_code}] {event['title']}"

    print(f"\n✅ Found {len(events)} events:")
    print(f"   📖 {len([e for e in events if e['type'] == 'exam'])} exams/tests")
    print(f"   📝 {len([e for e in events if e['type'] == 'assignment'])} assignments/quizzes")

    # Generate HTML
    generate_html_calendar(events, breaks, semester_start, semester_end, args.output)

    print(f"\n🎉 Done! Opening {args.output}")

    # Open in browser
    import os
    os.system(f'open "{args.output}"')

if __name__ == '__main__':
    main()
