# CarePoint Hospital Management System

A small, deployable Hospital Management System demonstration built with **Python, Streamlit and SQLite**.

## Features
- Dashboard with patient, doctor, appointment and unpaid-bill counts
- Register and view patients
- Add and view doctors
- Schedule appointments and update their status
- Create bills and mark them as paid
- SQLite database is created automatically on first run

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the app:
   `streamlit run app.py`
5. Open the local URL printed in the terminal (usually http://localhost:8501).

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore`.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy.

## Deploy on Render
1. Create a GitHub repository and upload all project files, including `render.yaml`.
2. In Render, choose **New + → Blueprint** and connect the repository, or create a Web Service manually.
3. If creating manually, use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Deploy.

## Important database note
This educational version uses a local SQLite file (`hospital.db`). On hosting platforms with an ephemeral filesystem, records may reset after a restart or redeploy. For durable multi-user data, connect a managed database such as PostgreSQL (for example, Render Postgres or Supabase) before using it beyond a classroom demo.

## Safety and scope
This is a classroom prototype, not a real hospital information system. Use fictional sample data only. It has no authentication, encryption, audit trail, backups, role-based permissions, or clinical decision support. Do not enter real patient or medical information.
