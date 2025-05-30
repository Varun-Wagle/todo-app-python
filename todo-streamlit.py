import streamlit as st
import os
import hashlib
from datetime import datetime

#----------- Fonts Use -----------

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans&family=Raleway:wght@400;700&display=swap');

    /* General UI Font: Raleway */
    html, body, [class*="css"] {
        font-family: 'Raleway', sans-serif;
    }

    /* Input Fields Font: Open Sans */
    input, textarea {
        font-family: 'Open Sans', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)


#----------- Utilities -----------
def get_user_file(username):
    return f"{username}_login.txt"

def get_task_file(username):
    return f"tasks_{username}.txt"

def get_done_file(username):
    return f"doneTasks_{username}.txt"

def get_settings_file(username):
    return f"settings_{username}.txt"

def save_auto_delete_setting(username, auto_delete):
    with open(get_settings_file(username), "w") as f:
        f.write(str(auto_delete))

def load_auto_delete_setting(username):
    if os.path.exists(get_settings_file(username)):
        with open(get_settings_file(username), "r") as f:
            return f.read().strip().lower() == "true"
        return False # Default if file doesn't exist

# Hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verify Password
def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Load Tasks
def load_tasks(file):
    tasks = {}
    if os.path.exists(file):
        with open(file, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    task, priority = parts
                    tasks[task] = priority
    return tasks


#------------ Auto Delete Feature ------------
def load_done_tasks(file, auto_delete=False):
    tasks = {}
    if os.path.exists(file):
        lines = open(file).readlines()
        with open(file, "w") as f:
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    task, priority, timestamp = parts
                    task_date = datetime.fromisoformat(timestamp)
                    if auto_delete and (datetime.now() - task_date).days > 90:
                        continue # Skip old tasks
                    tasks[task] = (priority, timestamp)
                    f.write(line)
    return tasks


# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "new_user" not in st.session_state:
    st.session_state.new_user = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auto_delete" not in st.session_state:
    st.session_state.auto_delete =False
if "tasks" not in st.session_state:
    st.session_state.tasks = {}
if "done_tasks" not in st.session_state:
    st.session_state.done_tasks = {}
if "task_added_success" not in st.session_state:
    st.session_state.task_added_success = False
if "task_clear_success" not in st.session_state:
    st.session_state.task_clear_success = False

#------------ Welcome / Login Page ----------------
if not st.session_state.logged_in:
    st.title("📝 Welcome to the To-Do List App!")
    st.text("By Varun Wagle")
    st.subheader("🔐 Please Login!")

    username = st.text_input("Enter Your Username")
    
    if username:
        st.session_state.username = username
        user_file = get_user_file(username)

        if os.path.exists(user_file):
            # Existing User: Show password field
            password_input = st.text_input("Enter Your Password", type="password")
            if st.button("Login"):
                with open(user_file, "r") as f:
                    saved_password = f.read().strip()
                if verify_password(saved_password, password_input):
                    st.session_state.logged_in = True
                    st.success("Login Successful!")
                    st.session_state.tasks = load_tasks(get_task_file(username))
                    st.session_state.auto_delete = load_auto_delete_setting(username) # Load auto-delete state
                    st.session_state.done_tasks = load_done_tasks(get_done_file(username), auto_delete=False)
                    st.rerun()
                else:
                    st.error("Incorrect Password.") # Only show when the login button is clicked
        else:
            # New User Flow
            st.session_state.new_user = True
    
    if st.session_state.new_user:
        new_password = st.text_input("Set New Password", type="password")
        if st.button("Set Password"):
            if new_password:
                with open(get_user_file(st.session_state.username), "w") as f:
                    f.write(hash_password(new_password))
                st.success("Password Set. Please Log In.")
                st.session_state.new_user = False
                st.rerun()
            else:
                st.warning("Password cannot be empty.")
            
else:
    # User is logged in - Show the main App
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    tabs = st.tabs(["📝 Tasks", "✅ Completed Tasks", "➕ Add New Task", "⚙ Settings"])
    #----------- Tab 1: View Tasks --------------

    with tabs[0]:
        st.subheader("Your Tasks")
        if st.session_state.tasks:
            selected_tasks = []
            for task, priority in st.session_state.tasks.items():
                # Use a checkbox for each task
                if st.checkbox(f"{task} | Priority: {priority}", key=f"checkbox_{task}"):
                    selected_tasks.append(task)

            if st.button("Mark As Done"):
                if selected_tasks:
                    # Building a new dictionary excluding completed tasks
                    remaining_tasks = {t: p for t, p in st.session_state.tasks.items() if t not in selected_tasks}

                    # Save done tasks and update done_tasks state
                    with open(get_done_file(st.session_state.username), "a") as f:
                        for task in selected_tasks:
                            priority = st.session_state.tasks[task]
                            timestamp = datetime.now().isoformat()
                            f.write(f"{task}|{priority}|{timestamp}\n")
                            st.session_state.done_tasks[task] = (priority, timestamp)

                        # Replace session_state.tasks with remaining tasks
                        st.session_state.tasks = remaining_tasks
                        
                        # Rewrite the tasks file with remaining tasks
                        with open(get_task_file(st.session_state.username), "w") as f:
                            for t, p in remaining_tasks.items():
                                f.write(f"{t}|{p}\n")
                    st.success("Selected tasks marked as done!")
                    st.rerun()
                else:
                    st.warning("Please select at least one task to mark as done.")
        else:
            st.info("No active tasks")
    
    #----------- Tab 2: Completed Tasks --------------
    with tabs[1]:
        st.subheader("Completed Tasks")

        # Check auto-delete on every tab load if enabled
        if st.session_state.auto_delete:
            updated_done_tasks = {}
            with open(get_done_file(st.session_state.username), "w") as f:
                for task, (priority, timestamp) in st.session_state.done_tasks.items():
                    task_date = datetime.fromisoformat(timestamp)
                    if (datetime.now() - task_date).days <= 90:
                        updated_done_tasks[task] = (priority, timestamp)
                        f.write(f"{task}|{priority}|{timestamp}\n")
            st.session_state.done_tasks = updated_done_tasks


        if st.session_state.done_tasks:
            for task, value in st.session_state.done_tasks.items():
                if isinstance(value, tuple) and len(value) == 2:
                    priority, timestamp = value
                    completed_date = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
                    st.write(f"Task: {task}, Priority: {priority}, Completed On: {completed_date}")
                else:
                    # Handle Unexpected Data
                    st.warning(f"Corrupted Data for task: {task}")
        else:
            st.info("No completed tasks.")
    
    #----------- Tab 3: Add Tasks --------------
    with tabs[2]:
        st.subheader("Add New Task")
        new_task = st.text_input("Task")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        if st.button("Add Task"):
            if new_task:
                st.session_state.tasks[new_task] = priority
                with open(get_task_file(st.session_state.username), "a") as f:
                    f.write(f"{new_task}|{priority}\n")
                st.session_state.task_added_success = True # Mark Task added
                st.rerun()
        # Show success message after rerun
        if st.session_state.task_added_success:
            st.success("New Task Added Successfully!")
            st.session_state.task_added_success = False # Reset Flag
    
    #----------- Tab 4: Settings --------------
    with tabs[3]:
        st.subheader("Settings")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.tasks = {}
            st.session_state.done_tasks = {}
            st.rerun()
        if st.button("Clear All Data"):
            username = st.session_state.username
            # Remove tasks file
            task_file = get_task_file(username)
            if os.path.exists(task_file):
                os.remove(task_file)
            # Remove done file
            done_file = get_done_file(username)
            if os.path.exists(done_file):
                os.remove(done_file)
            # Clear session state
            st.session_state.tasks = {}
            st.session_state.done_tasks = {}
            st.session_state.task_clear_success = True
            st.rerun()
        # Show success message after clear rerun
        if st.session_state.task_clear_success:
            st.success("All Tasks Cleared!")
            st.session_state.task_clear_success = False

        #Auto-Delete Feature
        auto_delete_checkbox = st.checkbox("Enable Auto-Delete (Tasks older than 90 days)", value=st.session_state.auto_delete)
        if auto_delete_checkbox != st.session_state.auto_delete:
            st.session_state.auto_delete = auto_delete_checkbox
            save_auto_delete_setting(st.session_state.username, auto_delete_checkbox)