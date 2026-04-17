# Database Setup Instructions

## Overview
Planora now includes database persistence to save your calendar data across sessions. Your calendars are automatically saved and loaded using Supabase.

## Setup Steps

### 1. Run the Database Migration

1. Go to your Supabase project dashboard
2. Navigate to the **SQL Editor** in the left sidebar
3. Create a new query
4. Copy the entire contents of `supabase_migration.sql` and paste it into the editor
5. Click **Run** to execute the migration

### 2. Verify Tables Created

After running the migration, you should see two new tables in your database:

- **calendars** - Stores calendar metadata and HTML
  - Columns: id, user_id, semester_name, start_date, end_date, calendar_html, created_at, updated_at

- **courses** - Stores course information
  - Columns: id, calendar_id, course_code, course_name, pdf_filename, created_at

### 3. Row Level Security (RLS)

The migration automatically enables Row Level Security with policies that ensure:
- Users can only view their own calendars and courses
- Users can only modify their own data
- All operations are scoped to the authenticated user

## How It Works

### Auto-Save
When you generate a calendar:
1. The calendar HTML and metadata are automatically saved to your account
2. Course information is stored in the database
3. You'll see a success message confirming the save

### Auto-Load
When you log in:
1. Your most recent calendar is automatically loaded
2. The semester name, dates, and courses are restored
3. You'll see a "Loaded your saved calendar!" message

### Semester Name
You can optionally provide a semester name (e.g., "Fall 2024", "Spring 2025") to help identify your calendars. If you don't provide one, a default name will be generated.

## Troubleshooting

### "Generated calendar but failed to save" Error
This usually means there's an issue with the database tables or RLS policies. Verify that:
1. The migration was run successfully
2. The tables exist in your Supabase database
3. RLS policies are enabled

### Calendar Not Loading on Login
Check the browser console for errors. Common issues:
- Database tables not created
- Supabase credentials incorrect in `.env.local`
- RLS policies blocking access

### Multiple Calendars
Currently, the system saves one calendar per semester name. If you generate a new calendar with the same semester name, it will update the existing one.

## Future Enhancements
- Support for multiple saved calendars
- Calendar versioning and history
- Sharing calendars with other users
- Export saved calendars to ICS/PDF
