# 📅 Planora - Smart Syllabus Calendar

Plan smarter, achieve more with Planora - an intelligent syllabus calendar generator that transforms your course PDFs into a unified, interactive calendar.

## Features

- 📄 **Multi-Course Support**: Upload multiple syllabus PDFs at once
- 🔍 **Auto-Parse Course Codes**: Automatically extracts course codes from PDF filenames
- 📅 **Interactive Calendar**: Month-by-month navigation with a clean, modern interface
- 🔐 **Secure Authentication**: Email/password and Google OAuth sign-in via Supabase
- 🎨 **Clean UI**: Modern, neutral design with intuitive controls
- 📱 **Responsive**: Works on desktop and mobile devices

## Tech Stack

### Frontend
- React 18
- Supabase Auth
- Modern CSS with neutral color palette

### Backend
- Python 3
- Flask
- PDF parsing and date extraction
- Calendar generation

## Setup

### Prerequisites
- Node.js (v14+)
- Python 3.8+
- Supabase account

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip3 install flask flask-cors python-dateutil pypdf2 beautifulsoup4
```

3. Run the backend server:
```bash
python3 app.py
```

The backend will run on `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file with your Supabase credentials:
```env
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. Build and serve the production app:
```bash
npm run build
npx serve -s build -l 3000
```

The frontend will run on `http://localhost:3000`

### Supabase Configuration

1. Create a Supabase project at https://supabase.com
2. Enable Email authentication
3. (Optional) Enable Google OAuth:
   - Set up OAuth consent screen in Google Cloud Console
   - Create OAuth credentials
   - Add Supabase callback URL as authorized redirect URI
   - Add credentials to Supabase Auth settings

## Usage

1. Sign up or log in with email/password or Google
2. Enter your semester start and end dates
3. (Optional) Add university calendar URL
4. Upload syllabus PDFs - course codes will be auto-detected
5. Click "Generate Calendar"
6. Navigate through months using Previous/Next buttons
7. View all your assignments, exams, and deadlines in one place

## Project Structure

```
planora/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── improved_calendar.py   # Calendar generation logic
│   └── uploads/              # PDF upload directory
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth.js       # Authentication component
│   │   │   ├── Auth.css
│   │   │   ├── CalendarUpload.js  # Main calendar interface
│   │   │   └── CalendarUpload.css
│   │   ├── App.js
│   │   ├── AuthContext.js    # Supabase auth context
│   │   └── supabaseClient.js
│   └── package.json
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own needs.

## Author

Built with Claude Code
