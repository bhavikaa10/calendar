-- Supabase Migration for Planora Calendar Storage
-- Run this in your Supabase SQL Editor

-- Create calendars table to store user calendar data
CREATE TABLE IF NOT EXISTS calendars (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  semester_name VARCHAR(100) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  calendar_html TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, semester_name)
);

-- Create courses table to store individual course information
CREATE TABLE IF NOT EXISTS courses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  calendar_id UUID REFERENCES calendars(id) ON DELETE CASCADE NOT NULL,
  course_code VARCHAR(50) NOT NULL,
  course_name VARCHAR(200) NOT NULL,
  pdf_filename VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_calendars_user_id ON calendars(user_id);
CREATE INDEX IF NOT EXISTS idx_courses_calendar_id ON courses(calendar_id);

-- Enable Row Level Security
ALTER TABLE calendars ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

-- Create policies for calendars table
CREATE POLICY "Users can view their own calendars"
  ON calendars FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own calendars"
  ON calendars FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own calendars"
  ON calendars FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own calendars"
  ON calendars FOR DELETE
  USING (auth.uid() = user_id);

-- Create policies for courses table
CREATE POLICY "Users can view their own courses"
  ON courses FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM calendars
      WHERE calendars.id = courses.calendar_id
      AND calendars.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert their own courses"
  ON courses FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM calendars
      WHERE calendars.id = courses.calendar_id
      AND calendars.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update their own courses"
  ON courses FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM calendars
      WHERE calendars.id = courses.calendar_id
      AND calendars.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete their own courses"
  ON courses FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM calendars
      WHERE calendars.id = courses.calendar_id
      AND calendars.user_id = auth.uid()
    )
  );

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for calendars table
CREATE TRIGGER update_calendars_updated_at
  BEFORE UPDATE ON calendars
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
