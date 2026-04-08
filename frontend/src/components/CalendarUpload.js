import React, { useState, useEffect, useRef } from 'react';
import './CalendarUpload.css';

const CalendarUpload = () => {
  const [courses, setCourses] = useState([{ courseCode: '', file: null }]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [universityUrl, setUniversityUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [calendarHtml, setCalendarHtml] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [currentMonthIndex, setCurrentMonthIndex] = useState(0);
  const [totalMonths, setTotalMonths] = useState(0);
  const calendarRef = useRef(null);

  // Auto-extract course code from PDF filename
  const extractCourseCode = (filename) => {
    // Remove .pdf extension
    const nameWithoutExt = filename.replace(/\.pdf$/i, '');

    // Try to match common course code patterns (e.g., CS101, MATH-201, ENG 305)
    const patterns = [
      /([A-Z]{2,4}[\s-]?\d{3,4})/i,  // CS101, MATH-201, ENG 305
      /([A-Z]{2,4}\d{3,4})/i,         // CS101, MATH201
    ];

    for (const pattern of patterns) {
      const match = nameWithoutExt.match(pattern);
      if (match) {
        return match[1].replace(/[\s-]/g, '').toUpperCase();
      }
    }

    // If no pattern matches, return cleaned filename
    return nameWithoutExt.substring(0, 10).toUpperCase();
  };

  const addCourse = () => {
    setCourses([...courses, { courseCode: '', file: null }]);
  };

  const removeCourse = (index) => {
    const newCourses = courses.filter((_, i) => i !== index);
    setCourses(newCourses.length > 0 ? newCourses : [{ courseCode: '', file: null }]);
  };

  const updateCourse = (index, field, value) => {
    const newCourses = [...courses];

    if (field === 'file' && value) {
      // Auto-populate course code from filename if not already set
      const autoCourseCode = extractCourseCode(value.name);
      newCourses[index][field] = value;

      // Only auto-fill if course code is empty
      if (!newCourses[index].courseCode) {
        newCourses[index].courseCode = autoCourseCode;
      }
    } else {
      newCourses[index][field] = value;
    }

    setCourses(newCourses);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Validate inputs
      if (!startDate || !endDate) {
        throw new Error('Please provide start and end dates');
      }

      const validCourses = courses.filter(c => c.courseCode && c.file);
      if (validCourses.length === 0) {
        throw new Error('Please add at least one course with a PDF file');
      }

      // Create FormData
      const formData = new FormData();
      formData.append('start_date', startDate);
      formData.append('end_date', endDate);
      if (universityUrl) {
        formData.append('university_url', universityUrl);
      }

      validCourses.forEach(course => {
        formData.append('pdfs', course.file);
        formData.append('course_codes', course.courseCode);
      });

      // Send to backend
      const response = await fetch('http://localhost:5001/api/generate-calendar', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate calendar');
      }

      setSuccess(`Calendar generated successfully! Found ${data.total_events} events across ${data.num_courses} courses.`);
      setCalendarHtml(data.calendar_html);
      setCurrentMonthIndex(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle month navigation after calendar is rendered
  useEffect(() => {
    if (calendarHtml && calendarRef.current) {
      const monthContainers = calendarRef.current.querySelectorAll('.month-container');
      setTotalMonths(monthContainers.length);

      // Hide all months except the current one
      monthContainers.forEach((month, index) => {
        month.style.display = index === currentMonthIndex ? 'block' : 'none';
      });
    }
  }, [calendarHtml, currentMonthIndex]);

  const nextMonth = () => {
    if (currentMonthIndex < totalMonths - 1) {
      setCurrentMonthIndex(currentMonthIndex + 1);
    }
  };

  const prevMonth = () => {
    if (currentMonthIndex > 0) {
      setCurrentMonthIndex(currentMonthIndex - 1);
    }
  };

  return (
    <div className="calendar-upload">
      <h2>Generate Your Course Calendar</h2>
      <p className="subtitle">Upload your syllabus PDFs to create an integrated calendar</p>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="section">
          <h3>Semester Dates</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="startDate">Start Date</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="endDate">End Date</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="universityUrl">University Calendar URL (Optional)</label>
            <input
              id="universityUrl"
              type="url"
              placeholder="https://registrar.university.edu/academic-calendar"
              value={universityUrl}
              onChange={(e) => setUniversityUrl(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div className="section">
          <h3>Courses</h3>
          {courses.map((course, index) => (
            <div key={index} className="course-item">
              <div className="course-inputs">
                <div className="form-group">
                  <label>Course Code</label>
                  <input
                    type="text"
                    placeholder="CS101"
                    value={course.courseCode}
                    onChange={(e) => updateCourse(index, 'courseCode', e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="form-group file-input-group">
                  <label>Syllabus PDF</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => updateCourse(index, 'file', e.target.files[0])}
                    disabled={loading}
                  />
                  {course.file && <span className="file-name">{course.file.name}</span>}
                </div>
              </div>
              {courses.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeCourse(index)}
                  className="btn-remove"
                  disabled={loading}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={addCourse} className="btn-add" disabled={loading}>
            + Add Another Course
          </button>
        </div>

        <button type="submit" className="btn-submit" disabled={loading}>
          {loading ? 'Generating Calendar...' : 'Generate Calendar'}
        </button>
      </form>

      {calendarHtml && (
        <div className="calendar-result">
          <div className="result-header">
            <h2>Your Calendar</h2>
            <div className="header-actions">
              <div className="month-navigation">
                <button
                  onClick={prevMonth}
                  disabled={currentMonthIndex === 0}
                  className="nav-btn"
                  title="Previous Month"
                >
                  ← Previous
                </button>
                <span className="month-indicator">
                  Month {currentMonthIndex + 1} of {totalMonths}
                </span>
                <button
                  onClick={nextMonth}
                  disabled={currentMonthIndex === totalMonths - 1}
                  className="nav-btn"
                  title="Next Month"
                >
                  Next →
                </button>
              </div>
              <button
                onClick={() => {
                  setCalendarHtml('');
                  setSuccess('');
                  setCurrentMonthIndex(0);
                }}
                className="btn-secondary"
              >
                Clear Calendar
              </button>
            </div>
          </div>
          <div ref={calendarRef} className="calendar-display" dangerouslySetInnerHTML={{ __html: calendarHtml }} />
        </div>
      )}
    </div>
  );
};

export default CalendarUpload;
