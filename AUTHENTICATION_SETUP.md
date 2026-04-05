# Authentication & Export Setup Guide

## 🎉 What's Been Added

### ✅ Authentication Features
- **Email/Password Login** - Users can sign up with email
- **Google OAuth** - One-click sign in with Google
- **Session Management** - Automatic login persistence
- **Secure Backend** - Powered by Supabase

### ✅ Export Features
- **PDF Export** - Professional printable calendar
- **ICS Export** - Import to Google/Apple/Outlook Calendar
- **CSV Export** - Open in Excel or Google Sheets
- **JSON Export** - For developers and integrations

---

## 🚀 Setup Instructions

### Step 1: Create Supabase Account (Free)

1. Go to **https://supabase.com**
2. Click **"Start your project"**
3. Sign in with GitHub
4. Click **"New Project"**
5. Fill in:
   - **Name**: `syllabus-calendar` (or any name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Free
6. Click **"Create new project"** (takes ~2 minutes)

### Step 2: Get Your Supabase Keys

1. Once project is created, go to **Settings** (gear icon in sidebar)
2. Click **"API"** in the left menu
3. Find these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)
4. Keep this tab open, you'll need these!

### Step 3: Enable Google OAuth (Optional but Recommended)

1. In Supabase dashboard, go to **Authentication** → **Providers**
2. Find **Google** in the list
3. Toggle it **ON**
4. You'll need to create Google OAuth credentials:

#### Create Google OAuth App:
1. Go to **https://console.cloud.google.com**
2. Create a new project or select existing
3. Go to **APIs & Services** → **Credentials**
4. Click **"+ CREATE CREDENTIALS"** → **OAuth client ID**
5. Choose **"Web application"**
6. Fill in:
   - **Name**: SyllaSync
   - **Authorized redirect URIs**: Copy from Supabase (shown in the Google provider settings)
   - Example: `https://xxxxx.supabase.co/auth/v1/callback`
7. Click **"Create"**
8. Copy **Client ID** and **Client Secret**

#### Add to Supabase:
1. Back in Supabase, paste:
   - **Client ID** (from Google)
   - **Client Secret** (from Google)
2. Click **"Save"**

### Step 4: Configure Frontend

1. Create a `.env.local` file in the `frontend` directory:

\`\`\`bash
cd frontend
touch .env.local
\`\`\`

2. Add your Supabase credentials:

\`\`\`env
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key-here
\`\`\`

3. Replace with your actual values from Step 2

### Step 5: Update App.js to Include Auth

Update `frontend/src/App.js`:

\`\`\`javascript
import React from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import Auth from './components/Auth';
import ExportMenu from './components/ExportMenu';
import './App.css';

function AppContent() {
  const { user, signOut } = useAuth();

  // Show login if not authenticated
  if (!user) {
    return <Auth />;
  }

  // Your existing app content goes here
  return (
    <div className="App">
      <header>
        <h1>Welcome, {user.email}</h1>
        <button onClick={signOut}>Sign Out</button>
      </header>

      {/* Your existing calendar upload form */}

      {/* Add export menu after calendar is generated */}
      {events && events.length > 0 && (
        <ExportMenu
          events={events}
          semesterInfo="Fall 2025: Sept 1 - Dec 15"
        />
      )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
\`\`\`

### Step 6: Install Dependencies (Already Done!)

The following packages have been installed:
- `@supabase/supabase-js` - Authentication
- `jspdf` & `jspdf-autotable` - PDF export
- `ics` - Calendar file export

### Step 7: Start Development Server

\`\`\`bash
cd frontend
npm start
\`\`\`

---

## 🎨 How to Use

### Authentication

**Sign Up with Email:**
1. Enter email and password
2. Click "Sign Up"
3. Check email for confirmation link
4. Click link to verify
5. Return to app and sign in

**Sign In with Google:**
1. Click "Continue with Google"
2. Choose Google account
3. Allow permissions
4. Automatically signed in!

### Export Calendar

**After generating your calendar:**
1. Click **"Export Calendar"** button
2. Choose format:
   - **PDF** - For printing or saving
   - **ICS** - To add to calendar apps
   - **CSV** - For Excel/Sheets
   - **JSON** - For developers
3. File downloads automatically!

**Import ICS to Google Calendar:**
1. Export as ICS from app
2. Go to Google Calendar
3. Click **"+"** next to "Other calendars"
4. Select **"Import"**
5. Upload the `.ics` file
6. Done! All events added

---

## 🔒 Security Notes

### Environment Variables
- **NEVER** commit `.env.local` to git
- Already added to `.gitignore`
- Use different keys for production

### Supabase Security
- Free tier: 50,000 monthly active users
- Automatic SSL/HTTPS
- Row Level Security (RLS) enabled
- Email verification required

---

## 🚀 Deployment

### Deploy to Vercel with Auth

1. Push code to GitHub
2. Go to **https://vercel.com**
3. Import your repository
4. Add environment variables:
   - `REACT_APP_SUPABASE_URL`
   - `REACT_APP_SUPABASE_ANON_KEY`
5. Deploy!

### Update Google OAuth for Production

1. Go to Google Cloud Console
2. Add production URL to **Authorized redirect URIs**:
   - `https://your-app.vercel.app`
3. Update Supabase redirect URL settings

---

## 📊 Database Schema (Optional - for saving calendars)

If you want users to save their calendars to the cloud:

\`\`\`sql
-- Run in Supabase SQL Editor

create table calendars (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  semester_start date,
  semester_end date,
  events jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Enable Row Level Security
alter table calendars enable row level security;

-- Users can only see their own calendars
create policy "Users can view own calendars"
  on calendars for select
  using (auth.uid() = user_id);

create policy "Users can insert own calendars"
  on calendars for insert
  with check (auth.uid() = user_id);

create policy "Users can update own calendars"
  on calendars for update
  using (auth.uid() = user_id);

create policy "Users can delete own calendars"
  on calendars for delete
  using (auth.uid() = user_id);
\`\`\`

---

## 🆘 Troubleshooting

### "Invalid API key" error
- Check `.env.local` has correct values
- Restart development server: `npm start`

### Google sign-in not working
- Verify redirect URI in Google Console matches Supabase
- Check Google OAuth is enabled in Supabase

### Export not working
- Check browser console for errors
- Ensure events array is populated
- Try different export format

### Can't sign in after sign up
- Check email for verification link
- Check spam folder
- Resend verification from Supabase dashboard

---

## 🎯 Next Steps

1. **Save calendars to database** - Use schema above
2. **Add profile page** - Let users update email/password
3. **Share calendars** - Generate shareable links
4. **Mobile app** - Build with React Native
5. **Notifications** - Email reminders for deadlines

---

## 📝 Support

- Supabase Docs: https://supabase.com/docs
- Auth Guide: https://supabase.com/docs/guides/auth
- Questions? Check issues on GitHub

Happy scheduling! 🎓
