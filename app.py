import sqlite3
from datetime import date, datetime
import streamlit as st
import pandas as pd

DB_PATH = "hospital.db"

st.set_page_config(page_title="CarePoint Hospital", page_icon="🏥", layout="wide")

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with connect() as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, age INTEGER NOT NULL, gender TEXT,
            phone TEXT, condition TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, specialization TEXT NOT NULL,
            phone TEXT, availability TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL, doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL, appointment_time TEXT NOT NULL,
            reason TEXT, status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL, description TEXT NOT NULL,
            amount REAL NOT NULL, bill_date TEXT NOT NULL,
            paid INTEGER DEFAULT 0,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )""")
        con.commit()

def query(sql, params=()):
    with connect() as con:
        return pd.read_sql_query(sql, con, params=params)

def execute(sql, params=()):
    with connect() as con:
        cur = con.cursor()
        cur.execute(sql, params)
        con.commit()
        return cur.lastrowid

init_db()

st.sidebar.title("🏥 CarePoint")
page = st.sidebar.radio("Navigation", [
    "Dashboard", "Patients", "Doctors", "Appointments", "Billing"
])
st.sidebar.caption("Hospital Management System • College demonstration")

if page == "Dashboard":
    st.title("🏥 CarePoint Hospital Management")
    st.write("A simple working demonstration for managing hospital records.")
    p = query("SELECT COUNT(*) n FROM patients").iloc[0]["n"]
    d = query("SELECT COUNT(*) n FROM doctors").iloc[0]["n"]
    a = query("SELECT COUNT(*) n FROM appointments WHERE status='Scheduled'").iloc[0]["n"]
    unpaid = query("SELECT COALESCE(SUM(amount),0) n FROM bills WHERE paid=0").iloc[0]["n"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered patients", int(p))
    c2.metric("Doctors", int(d))
    c3.metric("Scheduled appointments", int(a))
    c4.metric("Unpaid bills", f"₹{unpaid:,.2f}")
    st.subheader("Recent appointments")
    recent = query("""SELECT a.id, p.name AS patient, d.name AS doctor,
                      a.appointment_date, a.appointment_time, a.status
                      FROM appointments a
                      JOIN patients p ON p.id=a.patient_id
                      JOIN doctors d ON d.id=a.doctor_id
                      ORDER BY a.appointment_date DESC, a.id DESC LIMIT 8""")
    st.dataframe(recent, use_container_width=True, hide_index=True)
    st.info("Demo only: use fictional patient information. This is not a real clinical system.")

elif page == "Patients":
    st.title("👥 Patient Management")
    with st.expander("➕ Register a patient", expanded=True):
        with st.form("patient_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name *")
            age = c2.number_input("Age *", min_value=0, max_value=120, step=1)
            gender = c1.selectbox("Gender", ["Not specified", "Female", "Male", "Other"])
            phone = c2.text_input("Phone")
            condition = st.text_input("Reason for visit / notes")
            submitted = st.form_submit_button("Save patient")
            if submitted:
                if not name.strip():
                    st.error("Please enter the patient's name.")
                else:
                    execute("INSERT INTO patients(name,age,gender,phone,condition) VALUES(?,?,?,?,?)",
                            (name.strip(), int(age), gender, phone.strip(), condition.strip()))
                    st.success("Patient registered.")
                    st.rerun()
    patients = query("SELECT id, name, age, gender, phone, condition FROM patients ORDER BY id DESC")
    st.subheader("Patient records")
    st.dataframe(patients, use_container_width=True, hide_index=True)
    if not patients.empty:
        with st.expander("Delete a patient record"):
            pid = st.selectbox("Patient ID", patients["id"].tolist(), key="delete_patient")
            if st.button("Delete patient"):
                execute("DELETE FROM bills WHERE patient_id=?", (int(pid),))
                execute("DELETE FROM appointments WHERE patient_id=?", (int(pid),))
                execute("DELETE FROM patients WHERE id=?", (int(pid),))
                st.success("Patient and related demo records deleted.")
                st.rerun()

elif page == "Doctors":
    st.title("🩺 Doctor Management")
    with st.form("doctor_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Doctor name *")
        specialty = c2.text_input("Specialization *")
        phone = c1.text_input("Phone")
        availability = c2.text_input("Availability", placeholder="Mon–Fri, 9 AM–2 PM")
        if st.form_submit_button("Add doctor"):
            if not name.strip() or not specialty.strip():
                st.error("Doctor name and specialization are required.")
            else:
                execute("INSERT INTO doctors(name,specialization,phone,availability) VALUES(?,?,?,?)",
                        (name.strip(), specialty.strip(), phone.strip(), availability.strip()))
                st.success("Doctor added.")
                st.rerun()
    doctors = query("SELECT id, name, specialization, phone, availability FROM doctors ORDER BY id DESC")
    st.subheader("Doctor directory")
    st.dataframe(doctors, use_container_width=True, hide_index=True)
    if not doctors.empty:
        with st.expander("Remove a doctor"):
            did = st.selectbox("Doctor ID", doctors["id"].tolist(), key="delete_doctor")
            if st.button("Delete doctor"):
                execute("DELETE FROM appointments WHERE doctor_id=?", (int(did),))
                execute("DELETE FROM doctors WHERE id=?", (int(did),))
                st.success("Doctor and related demo appointments deleted.")
                st.rerun()

elif page == "Appointments":
    st.title("📅 Appointment Management")
    patients = query("SELECT id, name FROM patients ORDER BY name")
    doctors = query("SELECT id, name, specialization FROM doctors ORDER BY name")
    if patients.empty or doctors.empty:
        st.warning("Add at least one patient and one doctor before scheduling an appointment.")
    else:
        with st.form("appointment_form", clear_on_submit=True):
            pmap = {f'{r["name"]} (ID {r["id"]})': int(r["id"]) for _, r in patients.iterrows()}
            dmap = {f'{r["name"]} — {r["specialization"]} (ID {r["id"]})': int(r["id"]) for _, r in doctors.iterrows()}
            patient_label = st.selectbox("Patient", list(pmap))
            doctor_label = st.selectbox("Doctor", list(dmap))
            c1, c2 = st.columns(2)
            ap_date = c1.date_input("Date", min_value=date.today())
            ap_time = c2.time_input("Time")
            reason = st.text_input("Appointment reason")
            if st.form_submit_button("Schedule appointment"):
                execute("""INSERT INTO appointments(patient_id,doctor_id,appointment_date,appointment_time,reason)
                            VALUES(?,?,?,?,?)""",
                         (pmap[patient_label], dmap[doctor_label], ap_date.isoformat(), ap_time.strftime("%H:%M"), reason.strip()))
                st.success("Appointment scheduled.")
                st.rerun()
    appointments = query("""SELECT a.id, p.name AS patient, d.name AS doctor,
                            a.appointment_date, a.appointment_time, a.reason, a.status
                            FROM appointments a JOIN patients p ON p.id=a.patient_id
                            JOIN doctors d ON d.id=a.doctor_id ORDER BY a.appointment_date DESC, a.id DESC""")
    st.subheader("Appointments")
    st.dataframe(appointments, use_container_width=True, hide_index=True)
    if not appointments.empty:
        with st.expander("Update appointment status"):
            aid = st.selectbox("Appointment ID", appointments["id"].tolist())
            status = st.selectbox("New status", ["Scheduled", "Completed", "Cancelled"])
            if st.button("Update status"):
                execute("UPDATE appointments SET status=? WHERE id=?", (status, int(aid)))
                st.success("Appointment updated.")
                st.rerun()

elif page == "Billing":
    st.title("💳 Billing")
    patients = query("SELECT id, name FROM patients ORDER BY name")
    if patients.empty:
        st.warning("Register a patient before creating a bill.")
    else:
        with st.form("bill_form", clear_on_submit=True):
            pmap = {f'{r["name"]} (ID {r["id"]})': int(r["id"]) for _, r in patients.iterrows()}
            patient_label = st.selectbox("Patient", list(pmap))
            description = st.text_input("Description *", placeholder="Consultation / tests / room charges")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            bill_date = st.date_input("Bill date", value=date.today())
            if st.form_submit_button("Create bill"):
                if not description.strip() or amount <= 0:
                    st.error("Enter a description and an amount greater than zero.")
                else:
                    execute("INSERT INTO bills(patient_id,description,amount,bill_date) VALUES(?,?,?,?)",
                            (pmap[patient_label], description.strip(), float(amount), bill_date.isoformat()))
                    st.success("Bill created.")
                    st.rerun()
    bills = query("""SELECT b.id, p.name AS patient, b.description, b.amount,
                     b.bill_date, CASE WHEN b.paid=1 THEN 'Paid' ELSE 'Unpaid' END AS payment_status
                     FROM bills b JOIN patients p ON p.id=b.patient_id ORDER BY b.id DESC""")
    st.subheader("Bills")
    st.dataframe(bills, use_container_width=True, hide_index=True)
    if not bills.empty:
        unpaid_ids = query("SELECT id FROM bills WHERE paid=0")["id"].tolist()
        if unpaid_ids:
            with st.expander("Mark a bill as paid"):
                bid = st.selectbox("Unpaid bill ID", unpaid_ids)
                if st.button("Mark as paid"):
                    execute("UPDATE bills SET paid=1 WHERE id=?", (int(bid),))
                    st.success("Bill marked as paid.")
                    st.rerun()

st.sidebar.divider()
st.sidebar.caption("Educational prototype — not for real patient data or clinical decisions.")
