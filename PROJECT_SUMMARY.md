# MCA Project Summary

**Project title:** Smart Resume Screening Platform — TalentLens  
**Student:** Anshu Kumar Singh · **USN:** 1MV25MC006  
**Course:** MCA · **Guide:** Mrs. Sneha Bharti  
**Institution:** Sir M. Visvesvaraya Institute of Technology · **Academic year:** 2025–26

## Aim

Build a locally demonstrable recruitment application that compares candidate resumes with recruiter-defined job requirements and presents supporting evidence and score factors for human review.

## Main features

- Candidate, recruiter and admin workspaces with role-based access.
- Candidate/recruiter registrations are pending until approved or rejected by an admin.
- Candidates can upload replacement resume versions, delete uploaded files, apply using an active version, and update an existing application to the latest version.
- PDF and DOCX text extraction, skill detection, job applications, short skill assessments, score breakdowns and recruiter feedback.
- Recruiter job management and candidate review; admin account approval and summary dashboards.
- Responsive HTML/CSS/JavaScript interface, FastAPI backend, SQLite database and local resume file storage.
- Double-click Windows startup and stop scripts; no terminal interaction required for normal demonstration.

## Storage

`backend/data/platform.sqlite3` stores application records. `backend/data/uploads/` stores uploaded resume files. Both remain in the project directory across restarts.

## Research and evaluation

The project is an educational implementation informed by the IEEE INSPECT 2024 paper record “Optimizing Job Matching Through Automated Resume Screening with NLP and Machine Learning,” DOI 10.1109/INSPECT63485.2024.10896014. It uses a small skill vocabulary and TF-IDF similarity as a transparent baseline, not the paper's dataset or reported results. For final submission, evaluate against a consented or synthetic dataset and report suitable ranking and extraction metrics; do not claim accuracy until measured.

## Limitations

No OCR, transformer model, external credential verification, full production security hardening or validated fairness audit is included. Scores are review aids, not validated hiring measurements. Use synthetic or authorized data and do not use this prototype for real hiring decisions.
