import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { createEvent } from 'ics';

/**
 * Export calendar events to PDF
 * @param {Array} events - Array of event objects with {title, date, type}
 * @param {String} semesterInfo - Semester description
 */
export const exportToPDF = (events, semesterInfo = '') => {
  const doc = new jsPDF();

  // Add title
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text('Course Calendar', 14, 20);

  // Add semester info
  if (semesterInfo) {
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.text(semesterInfo, 14, 30);
  }

  // Prepare table data
  const tableData = events.map(event => [
    formatDate(event.date),
    event.type.toUpperCase(),
    event.title,
    event.courseCode || '-',
  ]);

  // Add table
  doc.autoTable({
    head: [['Date', 'Type', 'Event', 'Course']],
    body: tableData,
    startY: semesterInfo ? 35 : 30,
    theme: 'grid',
    headStyles: {
      fillColor: [102, 126, 234],
      fontSize: 11,
      fontStyle: 'bold',
    },
    styles: {
      fontSize: 10,
      cellPadding: 5,
    },
    columnStyles: {
      0: { cellWidth: 30 },
      1: { cellWidth: 25 },
      2: { cellWidth: 'auto' },
      3: { cellWidth: 25 },
    },
  });

  // Add footer
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    doc.text(
      `Page ${i} of ${pageCount}`,
      doc.internal.pageSize.getWidth() / 2,
      doc.internal.pageSize.getHeight() - 10,
      { align: 'center' }
    );
  }

  // Download
  doc.save('course-calendar.pdf');
};

/**
 * Export calendar events to ICS (iCalendar format)
 * Works with Google Calendar, Apple Calendar, Outlook
 * @param {Array} events - Array of event objects
 */
export const exportToICS = (events) => {
  const icsEvents = [];

  events.forEach(event => {
    const eventDate = new Date(event.date);
    const start = [
      eventDate.getFullYear(),
      eventDate.getMonth() + 1,
      eventDate.getDate(),
      0,
      0,
    ];

    const icsEvent = {
      start,
      duration: { hours: 1 },
      title: event.title,
      description: `${event.type.toUpperCase()}${event.courseCode ? ` - ${event.courseCode}` : ''}`,
      status: 'CONFIRMED',
      busyStatus: 'BUSY',
      categories: [event.type, event.courseCode].filter(Boolean),
    };

    icsEvents.push(icsEvent);
  });

  // Create ICS file for all events
  const promises = icsEvents.map(event => {
    return new Promise((resolve, reject) => {
      createEvent(event, (error, value) => {
        if (error) {
          reject(error);
        } else {
          resolve(value);
        }
      });
    });
  });

  Promise.all(promises)
    .then(values => {
      // Combine all events into one ICS file
      const icsContent = values.join('\n');
      const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'course-calendar.ics';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    })
    .catch(error => {
      console.error('Error creating ICS file:', error);
      alert('Error creating calendar file. Please try again.');
    });
};

/**
 * Export calendar events to CSV
 * @param {Array} events - Array of event objects
 */
export const exportToCSV = (events) => {
  const headers = ['Date', 'Type', 'Event', 'Course Code'];
  const rows = events.map(event => [
    event.date,
    event.type,
    `"${event.title.replace(/"/g, '""')}"`, // Escape quotes
    event.courseCode || '',
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(',')),
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'course-calendar.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export events in JSON format
 * @param {Array} events - Array of event objects
 */
export const exportToJSON = (events) => {
  const jsonContent = JSON.stringify(events, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'course-calendar.json';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Format date for display
 * @param {String} dateString - Date in YYYY-MM-DD format
 */
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};
