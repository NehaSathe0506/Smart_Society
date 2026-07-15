# Smart Society – Society Management System

A full-stack web application built with **Python, Flask, SQLite, HTML5, CSS3, and vanilla JavaScript** to digitalize daily operations of a residential housing society.

## Project Description

Smart Society replaces manual registers and paper-based society management with a centralized digital application. It manages residents, visitors, workers, worker attendance, notices, complaints, rental registrations, emergency contacts, and notifications — all through a role-based web dashboard.

## Problem Statement

Most residential societies still rely on paper registers to track visitor entries, worker attendance, complaints, and notices. This is inefficient, hard to search, and easy to lose. Smart Society solves this by providing a simple, centralized digital system accessible from any browser.

## Objectives

- Digitalize resident, visitor, and worker record-keeping
- Provide role-based access for Admins and Residents
- Enable residents to raise and track complaints online
- Maintain a digital notice board and notification system
- Track worker attendance with check-in/check-out timestamps
- Store emergency contact numbers for quick access

## Features

- Secure login with hashed passwords (SHA-256)
- Role-based access control (Admin / Resident)
- Resident CRUD with search
- Visitor entry/exit tracking
- Worker management with auto-generated Worker IDs
- Worker attendance (check-in/check-out) with history & filters
- Digital notice board with priority levels
- Complaint submission and status tracking
- Rental registration management
- Emergency contacts directory with click-to-call
- In-app notification system with unread counter
- Fully responsive design (desktop, tablet, mobile)

## User Roles

**Admin** – full access: manage residents, visitors, workers, attendance, notices, complaints, rentals, emergency contacts, and view the admin panel.

**Resident** – limited access: view notices, submit/track complaints, register rentals, view emergency contacts and notifications.

## Technology Stack

- Python 3
- Flask (backend web framework)
- SQLite (`sqlite3` standard library module)
- HTML5
- CSS3 (custom, no frameworks)
- Vanilla JavaScript

## Database Tables

1. `users` – login credentials and roles
2. `residents` – resident details
3. `visitors` – visitor entry/exit logs
4. `workers` – worker directory
5. `worker_attendance` – daily attendance records
6. `notices` – society notices
7. `complaints` – resident complaints
8. `rentals` – rental registrations
9. `emergency_contacts` – emergency numbers
10. `notifications` – system notifications

## Project Folder Structure

```
smart-society/
├── app.py
├── smart_society.db          (auto-created on first run)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── resident_dashboard.html
│   ├── residents.html
│   ├── resident_form.html
│   ├── resident_profile.html
│   ├── visitors.html
│   ├── visitor_form.html
│   ├── workers.html
│   ├── worker_form.html
│   ├── attendance.html
│   ├── attendance_history.html
│   ├── notices.html
│   ├── notice_form.html
│   ├── complaints.html
│   ├── complaint_form.html
│   ├── complaint_update.html
│   ├── rentals.html
│   ├── rental_form.html
│   ├── emergency.html
│   ├── emergency_form.html
│   ├── notifications.html
│   ├── admin.html
│   └── settings.html
├── static/
│   ├── css/style.css
│   └── js/script.js
└── README.md
```

## Installation Steps

**Step 1:** Open the project folder in VS Code.

**Step 2:** Open the VS Code terminal (``Ctrl + ` ``).

**Step 3:** Install Flask (only external dependency):

```
pip install flask
```

**Step 4:** Run the application:

```
python app.py
```

**Step 5:** Open your browser and go to:

```
http://127.0.0.1:5000
```

The database (`smart_society.db`) and sample data are created automatically the first time the app runs.

## Sample Login Credentials

**Admin**
Username: `admin`
Password: `admin123`

**Resident**
Username: `resident`
Password: `resident123`

## Project Modules

- Authentication & Session Management
- Resident Management
- Visitor Management
- Worker Management & Attendance
- Digital Notice Board
- Complaint Management
- Rental Registration
- Emergency Contacts
- Notification System
- Admin Panel
- Settings (Change Password)

## Future Enhancements

- Email/SMS notifications
- Bill and maintenance payment tracking
- Visitor photo capture
- Society event calendar
- Export reports to PDF/Excel

## Developer Section

**Developer:** Neha Sathe
**Course:** B.Tech Computer Science Engineering
**Project Type:** Third Year Mini Project
