import streamlit as st
import pandas as pd
import random
import os
from filelock import FileLock

# File to store assignments
ASSIGNMENTS_FILE = "test_jawahar_two_assignments.csv"
LOCK_FILE = "test_jawahar_two_assignments.lock"

# List of participants and their passcodes
staff_data = {
    "Participant": ["Nisha", "Jawahar", "Mahidhar"],
    "Passcode": ["N123", "J456", "M789"]  # Unique passcodes for each participant
}

# Initialize the assignments file if it doesn't exist
if not os.path.exists(ASSIGNMENTS_FILE):
    assignments_df = pd.DataFrame({
        "Participant": staff_data["Participant"],
        "Passcode": staff_data["Passcode"],
        "AssignedTo": [None] * len(staff_data["Participant"]),
        "Used": [False] * len(staff_data["Participant"])  # Track if the passcode has been used
    })
    assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)

# Title
st.title("Secure Gift Exchange: Test Jawahar Two")

# Input for participant's name and passcode
participant_name = st.text_input("Enter your name:")
participant_passcode = st.text_input("Enter your passcode (confidential):", type="password")

if st.button("Get Your Assignment"):
    # Use file lock to prevent simultaneous writes
    with FileLock(LOCK_FILE):
        # Load the assignments
        assignments_df = pd.read_csv(ASSIGNMENTS_FILE)

        if participant_name not in assignments_df["Participant"].values:
            st.error("Your name is not on the list. Please contact the organizer.")
        else:
            # Verify passcode
            stored_passcode = assignments_df.loc[assignments_df["Participant"] == participant_name, "Passcode"].values[0]
            used_status = assignments_df.loc[assignments_df["Participant"] == participant_name, "Used"].values[0]

            if participant_passcode != stored_passcode:
                st.error("Incorrect passcode. Please try again.")
            elif used_status:
                st.error("This username and passcode have already been used. Attempts are over.")
            else:
                # Check if this participant already has an assignment
                current_assignment = assignments_df.loc[assignments_df["Participant"] == participant_name, "AssignedTo"].values[0]
                if pd.notna(current_assignment):
                    st.info(f"You have already been assigned: {current_assignment}")
                else:
                    # Get available names (those not already assigned)
                    available_names = assignments_df.loc[assignments_df["AssignedTo"].isna(), "Participant"].tolist()
                    available_names = [name for name in available_names if name != participant_name]

                    if not available_names:
                        st.error("No more names available to assign!")
                    else:
                        # Randomly assign a name
                        assigned_name = random.choice(available_names)
                        assignments_df.loc[assignments_df["Participant"] == participant_name, "AssignedTo"] = assigned_name
                        assignments_df.loc[assignments_df["Participant"] == participant_name, "Used"] = True  # Mark as used

                        # Save the updated assignments immediately to ensure consistency
                        assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)
                        st.success(f"You have been assigned: {assigned_name}")

# For the organizer (optional): View all assignments
if participant_name == "Nisha" and participant_passcode == "N123":
    if st.checkbox("Show all assignments (Organizer Only)"):
        with FileLock(LOCK_FILE):
            assignments_df = pd.read_csv(ASSIGNMENTS_FILE)
            st.write(assignments_df)
