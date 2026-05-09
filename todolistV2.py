import json
import os
from datetime import datetime

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

tasks = load_tasks()

def show_menu():
    print("\n" + "="*40)
    print("        TO-DO LIST MANAGER")
    print("="*40)
    print("1. Add task")
    print("2. View all tasks")
    print("3. View incomplete tasks")
    print("4. Mark task as complete")
    print("5. Delete task")
    print("6. Exit")
    print("="*40)

def add_task():
    print("\n--- ADD NEW TASK ---")
    task = input("Enter task description: ")
    due_date = input("Due date (YYYY-MM-DD) or press Enter to skip: ")
    
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("[!] Invalid date format! Task added without due date.")
            due_date = ""
    
    new_task = {
        "task": task,
        "due": due_date if due_date else "No due date",
        "done": False,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    tasks.append(new_task)
    save_tasks()
    print("[+] Added: '" + task + "'")

def view_tasks(show_all=True, show_completed=False):
    if len(tasks) == 0:
        print("\n[!] Your to-do list is empty!")
        return False
    
    if not show_all:
        if show_completed:
            filtered = [t for t in tasks if t["done"]]
            title = "COMPLETED TASKS"
        else:
            filtered = [t for t in tasks if not t["done"]]
            title = "INCOMPLETE TASKS"
    else:
        filtered = tasks
        title = "ALL TASKS"
    
    if len(filtered) == 0:
        print("\n[!] No " + title.lower() + " found!")
        return False
    
    print("\n" + "-"*50)
    print(title.center(50))
    print("-"*50)
    
    for i, task in enumerate(filtered, start=1):
        original_index = tasks.index(task) + 1
        
        status = "[X]" if task["done"] else "[ ]"
        
        if task['due'] != "No due date":
            due_display = " [Due: " + task['due'] + "]"
        else:
            due_display = ""

        overdue = ""
        if not task["done"] and task["due"] != "No due date":
            try:
                due_date = datetime.strptime(task["due"], "%Y-%m-%d")
                if due_date < datetime.now():
                    overdue = " [OVERDUE]"
            except:
                pass
        
        print(str(i) + ". " + status + " " + task['task'] + due_display + overdue)
        print("   Created: " + task['created'])
    
    print("-"*50)
    return True

def mark_complete():
    if len(tasks) == 0:
        print("\n[!] No tasks to mark as complete!")
        return
    
    incomplete = [t for t in tasks if not t["done"]]
    
    if len(incomplete) == 0:
        print("\n[!] All tasks are already complete! Great job!")
        return
    
    print("\n--- MARK TASK AS COMPLETE ---")
    print("\nIncomplete tasks:")
    for i, task in enumerate(incomplete, start=1):
        if task['due'] != "No due date":
            due_info = " (Due: " + task['due'] + ")"
        else:
            due_info = ""
        print(str(i) + ". " + task['task'] + due_info)
    
    try:
        choice = int(input("\nEnter task number to mark as complete (0 to cancel): "))
        if choice == 0:
            print("Cancelled.")
            return
        if 1 <= choice <= len(incomplete):
            task_to_complete = incomplete[choice - 1]
            for task in tasks:
                if task is task_to_complete:
                    task["done"] = True
                    break
            save_tasks()
            print("[+] Marked as complete: '" + task_to_complete['task'] + "'")
        else:
            print("[!] Invalid number! Choose 1-" + str(len(incomplete)))
    except ValueError:
        print("[!] Please enter a valid number!")

def delete_task():
    if len(tasks) == 0:
        print("\n[!] Nothing to delete!")
        return
    
    view_tasks()
    
    try:
        task_num = int(input("\nEnter task number to delete (0 to cancel): "))
        if task_num == 0:
            print("Cancelled.")
            return
        if 1 <= task_num <= len(tasks):
            removed = tasks.pop(task_num - 1)
            save_tasks()
            print("[-] Deleted: '" + removed['task'] + "'")
        else:
            print("[!] Invalid number! Choose 1-" + str(len(tasks)))
    except ValueError:
        print("[!] Please enter a valid number!")

def main():
    print("\n[TASK MANAGER] WELCOME TO YOUR PERSONAL TASK MANAGER!")
    print("Loaded " + str(len(tasks)) + " existing tasks.")
    
    while True:
        show_menu()
        choice = input("Choose an option (1-6): ")
        
        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks(show_all=True)
        elif choice == "3":
            view_tasks(show_all=False, show_completed=False)
        elif choice == "4":
            mark_complete()
        elif choice == "5":
            delete_task()
        elif choice == "6":
            save_tasks()
            print("\n[+] Saved " + str(len(tasks)) + " tasks.")
            print("[TASK MANAGER] Goodbye! Have a productive day!")
            break
        else:
            print("[!] Invalid choice! Please enter 1, 2, 3, 4, 5, or 6.")

# Run the program
if __name__ == "__main__":
    main()