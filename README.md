# BedStats – Hospital Bed Management System

## Overview

BedStats is a Django-based hospital bed management and statistics system designed to help hospitals manage beds, patients, admissions, discharges, transfers, deaths, and hospital reports efficiently.

## Main Features

- Hospital bed management
- 120 hospital beds across 4 wards
- Real-time bed status management
- Patient registration and management
- Patient admissions
- Patient discharges
- Patient transfers
- Recording of deaths
- Patient movement tracking
- Hospital bed statistics and reports
- Excel report export
- PDF report export
- User login and authentication
- Role-based access control
- Professional dashboard
- Access denied (403) page

## Wards

The system contains four wards:

| Ward | Abbreviation | Beds |
|---|---|---:|
| Childrens Ward | CW | 30 |
| Mental Health Unit Ward | MHU | 30 |
| Female Ward | FW | 30 |
| Male Ward | MW | 30 |
| **Total** | | **120** |

## Bed Statuses

Beds can have the following statuses:

- Available
- Occupied
- Reserved
- Cleaning
- Out of Service

## Patient Information

The system records:

- Patient number
- First name
- Last name
- Sex
- Age
- Diagnosis
- Registration date

## Admission Management

Admission records include:

- Patient
- Bed
- Admission date
- Expected discharge date
- Diagnosis
- Attending department
- Admission status

## User Roles

The system supports different user roles with controlled access to system functions, including:

- Administrator
- Health Information Officer
- Matron/Nurse
- Records Officer
- Doctor
- Management

## Technologies Used

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- Bootstrap

## Project Structure

```text
bedstats/
│
├── beds/
│   ├── migrations/
│   ├── management/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── tests.py
│
├── bedstats/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
└── README.md