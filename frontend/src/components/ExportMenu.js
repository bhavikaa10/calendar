import React, { useState } from 'react';
import { exportToPDF, exportToICS, exportToCSV, exportToJSON } from '../utils/exportUtils';
import './ExportMenu.css';

const ExportMenu = ({ events, semesterInfo }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!events || events.length === 0) {
    return null;
  }

  const handleExport = (format) => {
    switch (format) {
      case 'pdf':
        exportToPDF(events, semesterInfo);
        break;
      case 'ics':
        exportToICS(events);
        break;
      case 'csv':
        exportToCSV(events);
        break;
      case 'json':
        exportToJSON(events);
        break;
      default:
        break;
    }
    setIsOpen(false);
  };

  return (
    <div className="export-menu">
      <button
        className="export-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Export Calendar
      </button>

      {isOpen && (
        <>
          <div className="export-overlay" onClick={() => setIsOpen(false)} />
          <div className="export-dropdown">
            <div className="export-header">
              <h3>Export Calendar</h3>
              <p>Choose your preferred format</p>
            </div>

            <button
              className="export-option"
              onClick={() => handleExport('pdf')}
            >
              <div className="export-icon pdf">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
              </div>
              <div className="export-info">
                <strong>PDF Document</strong>
                <span>Printable calendar with all events</span>
              </div>
            </button>

            <button
              className="export-option"
              onClick={() => handleExport('ics')}
            >
              <div className="export-icon ics">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </div>
              <div className="export-info">
                <strong>ICS Calendar File</strong>
                <span>Import to Google/Apple/Outlook Calendar</span>
              </div>
            </button>

            <button
              className="export-option"
              onClick={() => handleExport('csv')}
            >
              <div className="export-icon csv">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="10" y1="13" x2="10" y2="17" />
                  <line x1="14" y1="13" x2="14" y2="17" />
                </svg>
              </div>
              <div className="export-info">
                <strong>CSV Spreadsheet</strong>
                <span>Open in Excel or Google Sheets</span>
              </div>
            </button>

            <button
              className="export-option"
              onClick={() => handleExport('json')}
            >
              <div className="export-icon json">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="16 18 22 12 16 6" />
                  <polyline points="8 6 2 12 8 18" />
                </svg>
              </div>
              <div className="export-info">
                <strong>JSON Data</strong>
                <span>For developers and integrations</span>
              </div>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ExportMenu;
