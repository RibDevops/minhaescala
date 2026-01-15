# Sistema de Escalas - Django Calendar Application

## Overview
A Django-based scheduling/shift management system (Sistema de Escalas) for organizing and viewing work shifts (plantões). The application provides a calendar interface to view scheduled events by day.

## Project Structure
- `core/` - Django project settings and configuration
- `cal/` - Calendar application with event management
- `escala/` - Shift/schedule management application
- `templates/` - HTML templates
- `static/` - Static assets (JS, CSS)

## Technology Stack
- Python 3.11
- Django 5.x
- SQLite database (db.sqlite3)
- Bootstrap for frontend styling

## Running the Application
The application runs on port 5000:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Database
Uses SQLite database stored in `db.sqlite3`. Migrations are managed through Django:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Key Features
- Calendar view with event display
- Shift/plantão creation and management
- Responsive interface for mobile devices

## Recent Changes
- 2026-01-15: Configured for Replit environment (locale handling, CSRF, frame options)
