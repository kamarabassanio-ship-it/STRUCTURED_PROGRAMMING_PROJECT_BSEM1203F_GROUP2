# School Management System – Sierra Leone (SDG 4)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()

> **PROG103 – Principles of Structured Programming | Group 2 Final Project**  
> A fully functional, GUI‑driven school management system designed for educational institutions in Sierra Leone, aligning with **Sustainable Development Goal 4 (Quality Education)**.

---

## Project Overview

**School Management System** is a desktop application built with Python and Tkinter that provides a secure, user‑friendly platform for managing student records. It replaces paper‑based record‑keeping with a digital, searchable, and analytical system.

### Why This Project Matters

- **Real‑world impact**: Many schools in Sierra Leone still rely on paper records, leading to data loss, slow reporting, and difficulty in tracking student progress. This system digitises the entire process.
- **SDG alignment**: Directly supports **SDG 4 (Quality Education)** by improving school administration efficiency and enabling data‑driven decision‑making.
- **Open source**: Freely available for adaptation and improvement by the community.

---

## Key Features

### Authentication & Security
- Secure login with hashed passwords (SHA‑256)
- Multi‑role support (Admin / Teacher)
- "Forgot Password" guidance

### Dashboard
- Live KPI cards: **Total, Active, Inactive, Pending** records
- Recently added records (last 10)

### Full CRUD Operations
- **Create** – Add new student records with auto‑filled date and calendar picker
- **Read** – View all records with pagination (20 per page)
- **Update** – Edit existing records (right‑click or use Edit button)
- **Delete** – Remove records with confirmation (right‑click or Delete button)

### Advanced Search & Filters
- **Search** – Exact match by ID (numeric) or partial match by name
- **Filters** – Gender, Status, Date (Today / This Week / This Month / This Year)

### Data Visualisation
- **Pie Charts** – Gender distribution and Status breakdown
- **Bar Charts** – Status and Gender comparisons
- **Line Chart** – Monthly enrolment trends

### PDF Report Generation
- Custom date range (with calendar pickers for both start and end dates)
- Quick reports: **Weekly, Monthly, Yearly**
- Includes summary statistics, detailed tables, and generation timestamp

### Export & Backup
- Export records to CSV
- One‑click database backup

---

## Technology Stack

| Component          | Technology                                   |
|--------------------|----------------------------------------------|
| **GUI Framework**  | Tkinter + ttk (built‑in)                     |
| **Database**       | SQLite (lightweight, file‑based)             |
| **Charts**         | Matplotlib (with Seaborn style)              |
| **Data Handling**  | Pandas                                       |
| **PDF Generation** | FPDF                                         |
| **Language**       | Python 3.8+                                  |

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/kamarabassanio-ship-it/STRUCTURED_PROGRAMMING_PROJECT_BSEM1203F_GROUP2.git
cd STRUCTURED_PROGRAMMING_PROJECT_BSEM1203F_GROUP2