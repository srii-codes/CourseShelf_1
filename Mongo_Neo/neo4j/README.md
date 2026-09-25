# CourseShelf

A peer-to-peer textbook and notes circulation system built for college students. CourseShelf helps students find who owns a required book, discover compatible alternate editions, and track lending status — replacing informal, untracked channels like WhatsApp groups with a structured system.

## Problem

Students frequently need textbooks or notes that someone else in their batch already owns, but there's no structured way to find out who has it, whether an alternate edition would work, or when a currently borrowed book will be returned. This leads to redundant purchases and untracked, unreliable lending.

## Solution

CourseShelf lets students list books they own, search for what they need, and request to borrow — with the system automatically surfacing compatible alternate editions and tracing lending chains to show when an unavailable book is expected back.

## Architecture

This project uses a polyglot persistence approach — two databases, each handling the data access pattern it's best suited for:

- **MongoDB** — stores self-contained entity data: student profiles, book catalog, lending requests, and lending records
- **Neo4j** — models relationships as first-class data: edition compatibility between books, and student-to-student lending chains, enabling efficient multi-hop graph traversal queries

## Tech Stack

- **Database:** MongoDB (Atlas), Neo4j (AuraDB)
- **Backend:** Flask
- **Frontend:** React
- **Data generation:** Python + Faker (synthetic dataset)

## Data Model

### MongoDB Collections
- `students` — student_id, name, department, courses_enrolled, contact
- `books` — book_id, title, course_code, edition, condition, owner_id, status
- `lending_requests` — request_id, book_id, requester_id, status, requested_on
- `lending_records` — record_id, book_id, lender_id, borrower_id, borrowed_on, due_date, returned_on

### Neo4j Graph
- **Nodes:** `Student`, `Book`
- **Relationships:** `OWNS`, `EDITION_OF`, `LENT_TO {date, due_date}`

## Features

- Search for books by course code, title, or edition
- Automatic suggestion of compatible alternate editions
- Lending request, approval, and return tracking
- Graph-based traversal to trace current book holders and lending chains
- Aggregation-based analytics on demand vs. supply

## Project Structure

```text
courseshelf/
├── mongodb/     # MongoDB scripts, CRUD, aggregation queries
├── neo4j/       # Cypher scripts, CRUD, traversal queries
├── backend/     # API connecting both databases
├── frontend/    # Web interface
└── data/        # Faker scripts, sample datasets
```
## Setup

### MongoDB
1. Create a free MongoDB Atlas cluster
2. Update connection string in `mongodb/config.js` (or `.env`)
3. Run `node mongodb/seed.js` to load sample data

### Neo4j
1. Create a free Neo4j AuraDB instance
2. Update connection credentials in `neo4j/config.js` (or `.env`)
3. Run the Cypher seed script in `neo4j/seed.cypher` via Neo4j Browser or driver script

### Running the app
```bash
cd backend
npm install
npm start
```

## Team

- Rachita D (24BCE0937) — MongoDB (schema, CRUD, aggregation)
- Eshitha Vimalan (24BCE0921) — Neo4j (graph model, traversal queries)
- Sriranjani K (24BCE0946) — Backend integration & frontend

