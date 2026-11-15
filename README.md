# TalentLens — Smart Resume Screening Platform

An MCA demonstration project with candidate, recruiter and administrator workspaces. The app has a responsive HTML/CSS/JavaScript interface and a Python FastAPI backend. SQLite stores accounts, approvals, jobs, applications, scores and assessment records; uploaded resumes are kept as files in the same project data folder.

## Start the project without a terminal

1. Extract the project ZIP into a writable folder (for example, Documents).
2. Install Python 3.10 or newer once from [python.org](https://www.python.org/downloads/). In the installer, enable **Add Python to PATH**.
3. Double-click **`run.bat`** (or `start_talentlens.vbs`). It creates a private `.venv`, installs the required packages on the first launch, starts the local backend without a terminal window, and opens the app in your browser. The first setup needs an internet connection.
4. Use **`stop_talentlens.vbs`** when your demonstration is finished. Your data remains saved.

If Windows asks which app should open a `.vbs` file, choose **Windows Script Host**. If startup fails, inspect `backend/data/launcher.log`. `run_visible.bat` is available for troubleshooting and keeps a visible server window.

## Demo accounts

Local demo accounts are pre-approved so the application is ready to demonstrate immediately. Select one of the quick-access buttons on the sign-in screen; the demo password is `Demo123!`.

| Role | Email |
| --- | --- |
| Candidate | `candidate@demo.com` |
| Recruiter | `recruiter@demo.com` |
| Admin | `admin@demo.com` |

## Candidate and recruiter approval

1. On the sign-in page, choose **Create an account**.
2. Select Candidate or Recruiter and submit the registration form.
3. That account is saved with `pending` status. Login remains blocked until the admin acts.
4. Sign in through the Admin demo button, open **Users**, then select **Approve** or **Reject** for each pending account.
5. Approved users can sign in with their registered email and password.

## Recruiter job review

Recruiters can create a role directly from **Open roles**. Each role is submitted as pending for admin review in **Job approvals**; candidates see only approved roles. If an admin rejects a role, the recruiter can revise it from **Open roles** and resubmit it for another review.

While writing the job description, the role form suggests skills from the platform's built-in skill list and marks skills described as required or essential as high importance. Recruiters can add, remove, or edit skills and importance levels. Recruiter-authored assessment questions are optional; leave them blank to give candidates no quiz for that role.

Recruiter-written multiple-choice questions are optional. Roles without recruiter questions have no quiz. If questions are added, candidates receive those questions in a shuffled order and see their score after submission; recruiters see scores beside candidate names.

The local demonstration seeds a pre-approved admin account. For public deployment, use a separate deployment configuration and do not publish demo credentials.

## Change, replace or delete a resume

From a candidate account, open **My profile**. **Upload / replace resume** accepts text-based PDF and DOCX documents (up to 8 MB). Each upload becomes a new numbered version; earlier versions remain in history until deleted. Use **Delete** beside a version to remove that uploaded file. Application records and historic scores are retained; deleted versions cannot be used for new applications. A newer version can be applied to existing applications using **Use latest resume** on the Applications page.

Scanned PDFs without selectable text are not supported because OCR is not included. Use synthetic or authorized resume data for the academic demonstration.

## Database and stored files

Everything is stored locally in the extracted project folder:

```text
backend/data/platform.sqlite3   accounts, approvals, jobs, applications and scores
backend/data/uploads/             uploaded PDF/DOCX resume files
backend/data/launcher.log         setup and server messages
```

Do not move or delete `backend/data` while the app is running. To reset the demonstration, stop TalentLens and remove `backend/data`; the next start recreates the database and sample records.

## Demonstration sequence

1. Sign in as Admin and open **Users** to see approval controls.
2. Create a new account in a private/incognito browser window, attempt login, and show the pending approval message.
3. Approve it from the admin session and sign in as that account.
4. Sign in as Candidate, upload a PDF or DOCX, upload a revised file to create a new version, and delete an older version.
5. Explore the seeded job, apply, complete any recruiter-added quiz and view the score, if the role has one.
6. Sign in as Recruiter, create a role and type a description to see skill suggestions. Add optional custom assessment questions if needed.
7. Review the candidate by name, inspect the quiz score and extracted resume text, and record a decision.

## Project structure

```text
backend/main.py              FastAPI backend, SQLite, screening and scoring logic
frontend/index.html          App interface
frontend/styles.css          Responsive styling
frontend/app.js              Browser UI and API calls
launcher.py                  Quiet first-run setup and server launcher
start_talentlens.vbs          Double-click start entry point
stop_talentlens.vbs           Stops the app and preserves data
run.bat                       Double-click, quiet startup shortcut
start.bat                     Alternate quiet startup shortcut
run_visible.bat              Visible troubleshooting launcher
stop.py                       Safely stops the local server process
requirements.txt              Python dependencies
```

## Research and academic scope

The research topic follows the supplied project brief and the IEEE INSPECT 2024 paper record, “Optimizing Job Matching Through Automated Resume Screening with NLP and Machine Learning,” DOI [10.1109/INSPECT63485.2024.10896014](https://ieeexplore.ieee.org/document/10896014/). TalentLens is an independent educational prototype. It uses a small skill vocabulary and a transparent TF-IDF text similarity baseline; it does not claim to reproduce the paper’s dataset or results.

Scores organize information for human review and are not validated hiring measurements. The prototype does not include OCR, transformer models, external credential verification, production security hardening, or a validated fairness audit. Do not use it to make real hiring decisions.

## Academic details from the supplied brief

- **Project:** Smart Resume Screening Platform
- **Student:** Anshu Kumar Singh
- **USN:** 1MV25MC006
- **Course:** Master of Computer Applications (MCA)
- **Guide:** Mrs. Sneha Bharti
- **Institution:** Sir M. Visvesvaraya Institute of Technology (Sir MVIT)
- **Academic year:** 2025–26

Confirm these details with your department before submission.
