# Syllabus Calendar Extractor

A web application that automatically extracts important dates (assignments, exams, classes) from college syllabi and displays them in an interactive calendar.

## Features

- **PDF/DOCX/TXT Upload**: Upload syllabi in multiple formats
- **Intelligent Date Extraction**: Uses hybrid approach (local NLP + AI fallback)
- **Flexible Date Formats**: Handles specific dates, recurring patterns (e.g., "every Tuesday"), and relative dates
- **Semester Management**: Define semester start/end dates and breaks
- **URL Scraping**: Extract dates from school calendar websites
- **Interactive Calendar**: Visual calendar view with color-coded event types
- **Event Categorization**: Automatically categorizes events (exams, assignments, classes)

## Tech Stack

- **Frontend**: React with react-calendar
- **Backend**: Flask (Python)
- **Date Parsing**: dateparser, regex patterns
- **Document Processing**: PyPDF2, python-docx
- **AI Fallback**: Anthropic Claude API (optional)

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd syllabus-calendar-app/backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd syllabus-calendar-app/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will open at `http://localhost:3000`

## Usage

### Upload Syllabus Mode

1. Click "Upload File" tab
2. Select your syllabus file (PDF, DOCX, or TXT)
3. Enter semester start and end dates
4. (Optional) Add break periods (e.g., Spring Break, Thanksgiving)
5. (Optional) Enable AI fallback and provide Anthropic API key
6. Click "Extract Dates"

### URL Scraping Mode

1. Click "Scrape URL" tab
2. Enter the school calendar URL
3. Enter semester start and end dates
4. Click "Extract Dates"

### Features

- **Calendar View**: Visual representation of all events
- **Event List**: Detailed list sorted by date
- **Color Coding**:
  - Red: Exams
  - Blue: Assignments
  - Gray: Classes
  - Purple: Other events

## How It Works

### Local Date Extraction

The app first tries to extract dates using local libraries:

1. **Regex Patterns**: Matches common date formats (MM/DD/YYYY, Month DD, etc.)
2. **Dateparser**: Parses natural language dates
3. **Recurring Pattern Detection**: Identifies patterns like "every Tuesday"
4. **Context Analysis**: Uses keywords to categorize events

### AI Fallback

If local extraction finds fewer than 3 events and AI is enabled:

1. Sends syllabus text to Claude API
2. Uses LLM to intelligently extract dates and context
3. Handles complex date formats and implicit information

### Break Handling

- Events falling during defined break periods are automatically excluded
- Useful for recurring class meetings

## API Endpoints

### POST /api/upload
Upload and process a syllabus file

**Request**:
- `file`: Syllabus file (PDF/DOCX/TXT)
- `semester_start`: Start date (YYYY-MM-DD)
- `semester_end`: End date (YYYY-MM-DD)
- `breaks`: JSON array of break periods
- `use_ai`: Boolean for AI fallback
- `api_key`: Anthropic API key (if use_ai is true)

**Response**:
```json
{
  "success": true,
  "events": [
    {
      "title": "Assignment 1 Due",
      "date": "2024-09-15",
      "type": "assignment"
    }
  ],
  "extraction_method": "local"
}
```

### POST /api/scrape
Scrape dates from a URL

**Request**:
```json
{
  "url": "https://school.edu/calendar",
  "semester_start": "2024-09-01",
  "semester_end": "2024-12-15"
}
```

**Response**:
```json
{
  "success": true,
  "events": [...]
}
```

## Configuration

### AI Fallback (Optional)

To use the AI fallback feature:

1. Get an API key from [Anthropic](https://www.anthropic.com)
2. Enable "Use AI fallback" in the UI
3. Enter your API key
4. The AI will only be used if local extraction finds < 3 events

## Project Structure

```
syllabus-calendar-app/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Temporary file storage
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   └── package.json
└── README.md
```

## Limitations

- File size limit: 16MB
- AI extraction is optional and requires API key
- URL scraping may not work on all websites (depends on structure)
- Date extraction accuracy depends on syllabus formatting

## Future Enhancements

- Export to iCal (.ics) format
- Google Calendar integration
- Support for more file formats
- Machine learning model for better local extraction
- Timezone support
- Email reminders

## Troubleshooting

### Backend won't start
- Make sure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify port 5000 is not in use

### Frontend won't start
- Make sure Node.js 16+ is installed
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Verify port 3000 is not in use

### Date extraction not working
- Check that dates in syllabus are clearly formatted
- Try enabling AI fallback
- Verify semester dates are correct
- Make sure syllabus text is readable (not scanned images)

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
