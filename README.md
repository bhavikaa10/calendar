# Syllabus Calendar Generator

A web application that automatically extracts dates and deadlines from college syllabus PDFs and generates a beautiful, combined calendar view.

## Features

- **Multi-Syllabus Support**: Upload multiple course syllabi at once
- **Smart Date Extraction**: Automatically detects exams, assignments, quizzes, and deadlines
- **University Calendar Integration**: Scrape university websites to detect reading weeks, holidays, and breaks
- **Color-Coded Events**: Different colors for each course (assignments) while keeping exams consistent
- **Recurring Events**: Handles weekly assignments (e.g., "every Tuesday")
- **Combined View**: Merge all courses into a single calendar
- **Export**: Download as HTML file

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Backend**: Flask (Python)
- **Date Parsing**: Regex patterns + context analysis
- **Document Processing**: PyPDF2
- **Web Scraping**: BeautifulSoup, requests

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/syllabus-calendar-app.git
cd syllabus-calendar-app
```

2. Install dependencies:
```bash
pip3 install -r backend/requirements.txt
```

3. Run the backend:
```bash
cd backend
python3 app.py
```

4. Open `calendar_app.html` in your browser

## Usage

1. **Upload PDFs**: Click "Add Syllabus PDF" and select your course syllabi
2. **Enter Course Codes**: Provide course codes (e.g., STA302, ECO314) for each syllabus
3. **Set Dates**: Enter your semester start and end dates
4. **University Calendar** (Optional): Paste your university's academic calendar URL to auto-detect breaks
5. **Generate**: Click "Generate Combined Calendar"

The app will create a unified calendar showing all your courses with:
- Color-coded assignments by course
- All exams in red
- Reading weeks and holidays highlighted
- Weekly recurring assignments

## How It Works

1. **PDF Text Extraction**: Uses PyPDF2 to extract text from syllabus PDFs
2. **Pattern Matching**: Regex patterns detect various date formats:
   - "Monday, October 6, 2025"
   - "Oct 6"
   - "October 6th"
3. **Context Analysis**: Identifies event types based on surrounding keywords:
   - Term test, midterm, exam → Red (exam)
   - Assignment, quiz, reflection → Blue/Green/etc (course-specific)
4. **Recurring Events**: Generates weekly assignments automatically
5. **Break Detection**: Scrapes university calendar URL for reading weeks/holidays
6. **Calendar Merging**: Combines multiple courses while preserving break info

## Project Structure

```
syllabus-calendar-app/
├── backend/
│   ├── app.py              # Flask backend API
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/           # Temporary PDF storage
│   └── output/            # Generated calendars
├── improved_calendar.py    # Core calendar generation logic
├── calendar_app.html       # Web interface
└── README.md
```

## Deployment

The app can be deployed to various platforms. See platform-specific instructions:

### Render (Recommended - Free Tier)
1. Create account at render.com
2. Connect your GitHub repo
3. Create Web Service
4. Build command: `pip install -r backend/requirements.txt`
5. Start command: `cd backend && python app.py`
6. Deploy frontend (calendar_app.html) to static site

### Heroku
1. Add `Procfile` in backend: `web: python app.py`
2. Add `runtime.txt`: `python-3.11.0`
3. Deploy using Heroku CLI or GitHub integration

### Railway
Similar to Render - connect repo and deploy

## Technologies

- **Backend**: Python, Flask, PyPDF2, BeautifulSoup
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Calendar**: Python `calendar` module
- **Date Parsing**: Regex patterns + context analysis

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## License

MIT
