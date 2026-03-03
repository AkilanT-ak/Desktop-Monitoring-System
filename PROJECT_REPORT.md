# PROJECT REPORT

## 1. Introduction
This project focuses on implementing a desktop monitoring system capable of recording screen activity and generating reports. 
The primary goal is to understand automation, scheduling, cloud integration, and file handling in Python.

## 2. Objectives
- Implement screen recording module
- Generate periodic reports
- Implement offline storage
- Integrate cloud upload functionality

## 3. Modules

### 3.1 Screen Recording Module
Uses PyAutoGUI and OpenCV to capture frames and create MP4 output.

### 3.2 Report Module
Generates text logs and attaches video recordings.

### 3.3 Network Detection Module
Checks internet availability using socket connection.

### 3.4 Cloud Upload Module
Uploads large files to Google Drive if email size exceeds limit.

## 4. Working Principle
- Program runs continuously.
- At fixed intervals, recording starts.
- Report generated and sent.
- If internet unavailable, data stored locally.

## 5. Advantages
- Automated reporting
- Offline fallback mechanism
- Cloud integration support

## 6. Limitations
- Requires system resources
- Email size limit
- Requires proper security handling

## 7. Future Improvements
- Dashboard interface
- Secure authentication
- Encrypted logs
- Auto retry for pending reports

## 8. Ethical Considerations
Monitoring software must only be used with full consent.
Unauthorized usage may be illegal.
