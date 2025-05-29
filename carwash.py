import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# Simulated data stores
USERS_FILE = "users-carwash.csv"
CARS_FILE = "cars.csv"
JOBS_FILE = "jobs.csv"

# Load or initialize data
@st.cache_data
def load_data(file, columns):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame(columns=columns)

# Save data
def save_data(df, file):
    df.to_csv(file, index=False)

# Register user
def register_user(name, role, phone):
    users = load_data(USERS_FILE, ["user_id", "name", "role", "phone"])
    user_id = str(uuid.uuid4())
    users = pd.concat([users, pd.DataFrame([{
        "user_id": user_id, "name": name, "role": role, "phone": phone
    }])])
    save_data(users, USERS_FILE)
    return user_id

# Add a car
def add_car(user_id, plate, model):
    cars = load_data(CARS_FILE, ["car_id", "user_id", "plate", "model"])
    car_id = str(uuid.uuid4())
    cars = pd.concat([cars, pd.DataFrame([{
        "car_id": car_id, "user_id": user_id, "plate": plate, "model": model
    }])])
    save_data(cars, CARS_FILE)

# Request job
def request_wash(user_id, plate, location):
    jobs = load_data(JOBS_FILE, ["job_id", "customer_id", "plate", "location", "status", "cleaner_id", "timestamp"])
    job_id = str(uuid.uuid4())
    jobs = pd.concat([jobs, pd.DataFrame([{
        "job_id": job_id, "customer_id": user_id, "plate": plate,
        "location": location, "status": "Pending", "cleaner_id": "", "timestamp": datetime.now()
    }])])
    save_data(jobs, JOBS_FILE)

# Accept job
def accept_job(job_id, cleaner_id):
    jobs = load_data(JOBS_FILE, ["job_id", "customer_id", "plate", "location", "status", "cleaner_id", "timestamp"])
    jobs.loc[jobs["job_id"] == job_id, ["status", "cleaner_id"]] = ["In Progress", cleaner_id]
    save_data(jobs, JOBS_FILE)

# Complete job
def complete_job(job_id):
    jobs = load_data(JOBS_FILE, ["job_id", "customer_id", "plate", "location", "status", "cleaner_id", "timestamp"])
    jobs.loc[jobs["job_id"] == job_id, "status"] = "Completed"
    save_data(jobs, JOBS_FILE)

# UI Starts here
st.title("🚘 CarWash On-The-Go")

menu = st.sidebar.selectbox("Select Role", ["Register", "Customer", "Cleaner", "Admin"])

if menu == "Register":
    st.subheader("Register as Customer or Cleaner")
    name = st.text_input("Your Name")
    phone = st.text_input("Phone Number")
    role = st.selectbox("Role", ["Customer", "Cleaner"])
    if st.button("Register"):
        user_id = register_user(name, role, phone)
        st.success(f"Registered! Your ID: {user_id}")

elif menu == "Customer":
    st.subheader("🚙 Customer Dashboard")
    user_id = st.text_input("Enter your User ID")
    if user_id:
        action = st.radio("Select Action", ["Add Car", "Request Car Wash", "My Wash History"])
        
        if action == "Add Car":
            plate = st.text_input("Car Plate")
            model = st.text_input("Car Model")
            if st.button("Add Car"):
                add_car(user_id, plate, model)
                st.success("Car added!")
        
        elif action == "Request Car Wash":
            cars = load_data(CARS_FILE, ["car_id", "user_id", "plate", "model"])
            user_cars = cars[cars["user_id"] == user_id]
            selected_plate = st.selectbox("Select Car", user_cars["plate"] if not user_cars.empty else ["No car"])
            location = st.text_input("Enter Location")
            if st.button("Request Wash"):
                request_wash(user_id, selected_plate, location)
                st.success("Wash requested! Waiting for cleaner.")

        elif action == "My Wash History":
            jobs = load_data(JOBS_FILE, ["job_id", "customer_id", "plate", "location", "status", "cleaner_id", "timestamp"])
            my_jobs = jobs[jobs["customer_id"] == user_id]
            st.dataframe(my_jobs)

elif menu == "Cleaner":
    st.subheader("🧽 Cleaner Dashboard")
    cleaner_id = st.text_input("Enter your Cleaner ID")
    if cleaner_id:
        jobs = load_data(JOBS_FILE, ["job_id", "customer_id", "plate", "location", "status", "cleaner_id", "timestamp"])
        
        available_jobs = jobs[jobs["status"] == "Pending"]
        st.write("Available Jobs")
        st.dataframe(available_jobs)

        selected_job = st.text_input("Enter Job ID to Accept")
        if st.button("Accept Job"):
            accept_job(selected_job, cleaner_id)
            st.success("Job accepted!")

        my_jobs = jobs[jobs["cleaner_id"] == cleaner_id]
        st.write("My Jobs")
        st.dataframe(my_jobs)

        complete_id = st.text_input("Enter Job ID to Mark Complete")
        if st.button("Complete Job"):
            complete_job(complete_id)
            st.success("Job completed!")

elif menu == "Admin":
    st.subheader("📊 Admin Dashboard")
    jobs = load_data(JOBS_FILE, ["job_id", "customer_id", "plate", "location", "status", "cleaner_id", "timestamp"])
    st.write("All Jobs")
    st.dataframe(jobs)

    users = load_data(USERS_FILE, ["user_id", "name", "role", "phone"])
    st.write("Users")
    st.dataframe(users)
