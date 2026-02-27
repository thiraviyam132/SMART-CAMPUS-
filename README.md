# Smart Campus Issue Feedback & Tracking System

A full-stack starter project for reporting campus issues, tracking resolution status, and collecting user feedback.

## Project Structure

- `backend/` - Node.js + Express REST API
- `frontend/` - React + Vite + Tailwind client
- `backend/sql/schema.sql` - PostgreSQL schema

## Features (MVP)

- Role-aware authentication with JWT (`student`, `faculty`, `admin`, `staff`)
- Issue reporting with category, location, priority, and optional image URL
- Issue lifecycle tracking (`open`, `in_progress`, `resolved`, `closed`)
- Feedback and rating after resolution
- Dashboard metrics for admins

## Backend Setup

1. `cd backend`
2. `npm install`
3. Copy `.env.example` to `.env` and configure values
4. Create PostgreSQL database and run schema:
   - `psql -U postgres -d smart_campus -f sql/schema.sql`
5. Start server:
   - `npm run dev`

Backend runs on `http://localhost:5000` by default.

## Frontend Setup

1. `cd frontend`
2. `npm install`
3. Start app:
   - `npm run dev`

Frontend runs on `http://localhost:5173` by default.

## Suggested Next Steps

1. Add image upload support (Cloudinary or S3)
2. Add email/in-app notifications
3. Add map/QR-based location autofill
4. Add test suites (Jest + Supertest, React Testing Library)
