# Command-Line Tool Usage Guide

A simple CLI tool to extract dates from your syllabus without needing the web interface.

## Installation

First, install the required dependencies:

```bash
cd /Users/bhavikaagoenka/syllabus-calendar-app
pip install PyPDF2 python-docx dateparser anthropic
```

## Basic Usage

```bash
python extract_dates.py <file_path> --start YYYY-MM-DD --end YYYY-MM-DD
```

### Required Arguments:
- `file_path` - Path to your syllabus file (PDF, DOCX, or TXT)
- `--start` - Semester start date (format: YYYY-MM-DD)
- `--end` - Semester end date (format: YYYY-MM-DD)

## Examples

### Example 1: Basic Extraction

```bash
python extract_dates.py sample_syllabus.txt --start 2024-09-01 --end 2024-12-15
```

**Output:**
```
📄 Extracting dates from: sample_syllabus.txt
📅 Semester: 2024-09-01 to 2024-12-15
✓ Extracted 1234 characters
🔍 Using local extraction...

✅ Found 12 events:

Date            Type         Title
--------------------------------------------------------------------------------
Sep 03, 2024    class        Classes meet every Tuesday and Thursday from 10:00 AM
Sep 05, 2024    class        Classes meet every Thursday from 10:00 AM
Sep 19, 2024    assignment   Assignment 1 Due: September 19, 2024
Oct 03, 2024    exam         Quiz 1 on October 3, 2024
Oct 17, 2024    exam         Midterm Exam - October 17, 2024
Oct 22, 2024    assignment   Assignment 2 Due: October 22, 2024
Nov 07, 2024    exam         Quiz 2 - November 7, 2024
Nov 14, 2024    assignment   Assignment 3 Due: November 14, 2024
Dec 05, 2024    assignment   Final Project Due: December 5, 2024
Dec 12, 2024    exam         Final Exam: December 12, 2024 at 10:00 AM
```

### Example 2: With Break Periods

Exclude dates during breaks (like Thanksgiving or Spring Break):

```bash
python extract_dates.py sample_syllabus.txt \
    --start 2024-09-01 \
    --end 2024-12-15 \
    --break "Thanksgiving:2024-11-25:2024-11-29"
```

You can add multiple breaks:

```bash
python extract_dates.py syllabus.pdf \
    --start 2024-01-15 \
    --end 2024-05-10 \
    --break "Spring Break:2024-03-10:2024-03-17" \
    --break "Easter Break:2024-04-18:2024-04-22"
```

### Example 3: Use AI Extraction

For complex syllabi where local extraction might miss events:

```bash
python extract_dates.py syllabus.pdf \
    --start 2024-09-01 \
    --end 2024-12-15 \
    --ai \
    --api-key sk-ant-your-api-key-here
```

### Example 4: Different Output Formats

**Table format (default):**
```bash
python extract_dates.py sample_syllabus.txt --start 2024-09-01 --end 2024-12-15
```

**JSON format (for programmatic use):**
```bash
python extract_dates.py sample_syllabus.txt \
    --start 2024-09-01 \
    --end 2024-12-15 \
    --format json
```

Output:
```json
[
  {
    "title": "Assignment 1 Due: September 19, 2024",
    "date": "2024-09-19",
    "type": "assignment"
  },
  {
    "title": "Quiz 1 on October 3, 2024",
    "date": "2024-10-03",
    "type": "exam"
  }
]
```

**List format (with emojis):**
```bash
python extract_dates.py sample_syllabus.txt \
    --start 2024-09-01 \
    --end 2024-12-15 \
    --format list
```

Output:
```
📝 Sep 19, 2024 - Assignment 1 Due: September 19, 2024 (assignment)
📖 Oct 03, 2024 - Quiz 1 on October 3, 2024 (exam)
📖 Oct 17, 2024 - Midterm Exam - October 17, 2024 (exam)
```

## All Options

```
usage: extract_dates.py [-h] --start START --end END [--break BREAKS]
                        [--ai] [--api-key API_KEY]
                        [--format {table,json,list}]
                        file

positional arguments:
  file                  Path to syllabus file (PDF, DOCX, or TXT)

required arguments:
  --start START         Semester start date (YYYY-MM-DD)
  --end END             Semester end date (YYYY-MM-DD)

optional arguments:
  -h, --help            Show help message
  --break BREAKS        Break period (Name:YYYY-MM-DD:YYYY-MM-DD)
                        Can be used multiple times
  --ai                  Use AI extraction (requires --api-key)
  --api-key API_KEY     Anthropic API key for AI extraction
  --format {table,json,list}
                        Output format (default: table)
```

## Testing with Sample Syllabus

Try it out with the included sample syllabus:

```bash
python extract_dates.py sample_syllabus.txt \
    --start 2024-09-01 \
    --end 2024-12-15 \
    --break "Thanksgiving:2024-11-25:2024-11-29" \
    --format list
```

## Supported File Formats

- **PDF** (.pdf) - Most common format for syllabi
- **Word Documents** (.docx) - Microsoft Word files
- **Text Files** (.txt) - Plain text syllabi

## How It Works

1. **Text Extraction**: Extracts text from your document
2. **Pattern Matching**: Uses regex to find date patterns
3. **Date Parsing**: Intelligently parses various date formats:
   - "September 19, 2024"
   - "9/19/2024"
   - "19 Sept 2024"
   - "every Tuesday"
   - "all Thursdays"
4. **Event Classification**: Categorizes events as:
   - `assignment` - Homework, problem sets
   - `exam` - Tests, quizzes, midterms, finals
   - `class` - Regular class meetings
   - `other` - Everything else
5. **Break Filtering**: Excludes dates during specified breaks

## Tips for Best Results

1. **Clear Date Formats**: Syllabi with clear date formats work best
2. **Use Breaks**: Exclude break periods to avoid false class meetings
3. **Try AI Mode**: If local extraction misses events, try `--ai` mode
4. **JSON Output**: Use `--format json` to pipe into other tools

## Troubleshooting

**No events found:**
- Check that dates in your syllabus are within the semester range
- Try different date formats
- Use `--ai` mode for complex syllabi

**Too many events:**
- Add break periods with `--break`
- Check if recurring patterns are being over-matched

**API errors with --ai:**
- Verify your API key is correct
- Check you have Anthropic API credits

## Next Steps

Once you're happy with the extraction, you can:
1. Use the web interface for a better visual experience
2. Export to JSON and import into your calendar app
3. Deploy the full web app for sharing with classmates

Happy date extracting!
