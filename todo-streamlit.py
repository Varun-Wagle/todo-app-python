import streamlit as st
import os
# Call for datetime for autodelete feature
from datetime import datetime, timedelta

# Get Username Input
username = st.text_input("Enter your username: ")

# Initialize 
if username:
    task_file = f"tasks_{username}.txt"
    done_file = f"doneTasks_{username}.txt"


    # Load tasks
    def load_tasks(file):
        tasks = {}
        if os.path.exists(file):
            with open(file, "r") as f:
                for line in f:
                    task, priority = line.strip().split('|')
                    tasks[task] = priority
        return tasks

tasks = load_tasks(task_file)
done_tasks = load_tasks(done_file)

# Add new task
new_task = st.text_input("Add a new task: ")
priority = st.selectbox("Select priority:", ['Low', 'Medium', 'High'])
if st.button("Add Task"):
    if new_task:
        tasks[new_task] = priority
        with open(task_file, 'a') as f:
            f.write(f"{new_task}|{priority}\n")
        st.success("Task Added.")

#View Tasks
st.subheader("View Tasks:")
for task, priority in tasks.items():
    if st.button(f"Mark 'task' as done"):
        done_tasks[task] = priority
        tasks.pop(task)
        with open(done_file, 'a') as f:
            f.write(f"{task}|{priority}|{datetime.now()}\n")
        with open(task_file, 'w') as f:
            for t, p in tasks.items():
                f.write(f"Marked '{task}' as done!")

if tasks:
    for task, priority in tasks.items():
        st.write(f"Task: {task}, Priority: {priority}")
else:
    st.info("No active tasks.")

# View Completed Tasks
st.subheader("Completed Tasks.")
if done_tasks:
    for task, priority in done_tasks.items():
        st.write(f"Task: {task}, Priority: {priority}")
else:
    st.info("No Completed Tasks.")