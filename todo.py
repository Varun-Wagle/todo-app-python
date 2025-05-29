# Call for datetime for autodelete feature
from datetime import datetime, timedelta

# Initialize an empty list to hold tasks
tasks = [] # Each task is now a dict {'task': str, 'priority': str, 'done': bool}
username = input("Enter your username: ").strip()
tasks_file = f"tasks_{username}.txt"
done_file = f"doneTasks_{username}.txt"

# Load tasks from a file at startup
def load_tasks():
    try:
        with open(tasks_file, "r") as file:
            for line in file:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    task, priority, done_str = parts
                    done = done_str == "True"
                    tasks.append({'task': task, 'priority': priority, 'done': done})
    except FileNotFoundError:
        # File doesn't exist, so no tasks to load
        pass

# Save tasks to the file
def save_tasks():
    with open(tasks_file, "w") as file:
        for task_info in tasks:
            file.write(f"{task_info['task']}|{task_info['priority']}|{task_info['done']}\n")

# Display Tasks
def view_tasks(filter_type="all"):
    if not tasks:
        print("No tasks found.")
    else:
        print("\nYour Tasks:")
        for index, task_info in enumerate(tasks, start=1):
            if filter_type == "not_done" and task_info['done']:
                continue
            status = "✅ Done" if task_info['done'] else "❌ Not Done"
            print(f"{index}. {task_info['task']} (Priority: {task_info['priority']}), (Status: {status})")

# View only done tasks
def view_done_tasks():
    try:
        with open(done_file, "r") as file:
            lines = file.readlines()
            if not lines:
                print("No done tasks found.")
                return
            print("\nDone Tasks:")
            for index, line in enumerate(lines, start=1):
                parts = line.strip().split('|')
                if len(parts) == 3:
                    task, priority, timestamp = parts
                    print(f"{index}. {task} (Priority: {priority}, Completed On: {timestamp})")
    except FileNotFoundError:        
        print("No done tasks file found.")

# Adding New Task to File
def add_tasks():
    task = input("Enter a new task: ")
    priority = input("Enter priority (High/Medium/Low): ").capitalize()
    if priority not in ["High", "Medium", "Low"]:
        priority = "Low" # Default Priority
    tasks.append({'task': task, 'priority': priority, 'done': False})
    save_tasks()
    print(f"Task '{task}' added with priority '{priority}'.")

# Marking the tasks
def mark_task_done():
    view_tasks()
    try:
        task_num = int(input("Enter the task number to mark done: "))
        if 1 <= task_num <= len(tasks):
            done_task = tasks.pop(task_num - 1)
            save_tasks()

            # Add Timestamp
            timestamp = datetime.now().isoformat()
            with open(done_file, "a") as file:
                file.write(f"{done_task['task']}|{done_task['priority']}|{timestamp}\n")


            print(f"Task '{done_task['task']}' marked as done and moved to done tasks.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter valid number.")

# New auto-delete function
def clean_old_data():
    auto_delete = input("Auto-Delete tasks older than 90 days? [y/n]: ").lower() == 'y'
    if not auto_delete:
        return
    
    new_done_tasks = []
    try:
        with open(done_file, "r") as file:
            for line in file:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    task, priority, timestamp_str = parts
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if datetime.now() - timestamp < timedelta(days=90):
                        new_done_tasks.append(f"{task}|{priority}|{timestamp_str}\n")
    except FileNotFoundError:
        return
    
    with open(done_file, "w") as file:
        file.writelines(new_done_tasks)

# Step 6: Remove a task
def remove_tasks():
    view_tasks()
    try:
        task_num = int(input("Enter the task number to remove: "))
        if 1 <= task_num <= len(tasks):
            removed_task = tasks.pop(task_num - 1)
            save_tasks()
            print(f"Task '{removed_task['task']}' removed.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

# Step 7: Show Menu
def show_menu():
    print("\n----To Do List App----")
    print("1. View Tasks")
    print("2. Completed Tasks")
    print("3. Add Task")
    print("4. Delete Task")
    print("5. Mark Task as Done.")
    print("6. Exit")

# Step 8: Main Loop
# Call the Clean_Old_Data() when app starts:
def main():
    load_tasks()
    clean_old_data() # Clean up old done tasks
    while True:
        show_menu()
        choice = input("Enter your choice (1-5)")

        if choice == '1':
            view_tasks()
        elif choice == '2':
            view_done_tasks()
        elif choice == '3':
            add_tasks()
        elif choice == '4':
            remove_tasks()
        elif choice == '5':
            mark_task_done()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please Try Again.")

if __name__ == "__main__":
    main()
