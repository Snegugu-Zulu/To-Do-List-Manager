import json
import os
from datetime import datetime
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit, QDateEdit,
    QLabel, QMessageBox, QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon

TASKS_FILE = "tasks.json"

class Task:
    """Task data model"""
    def __init__(self, description, due_date=None, created=None, completed=False):
        self.description = description
        self.due_date = due_date  # Format: YYYY-MM-DD
        self.completed = completed
        self.created = created if created else datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        return {
            "description": self.description,
            "due_date": self.due_date,
            "completed": self.completed,
            "created": self.created
        }
    
    @staticmethod
    def from_dict(data):
        return Task(
            description=data["description"],
            due_date=data.get("due_date"),
            created=data.get("created"),
            completed=data.get("completed", False)
        )

class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.load_tasks()
        self.init_ui()
    
    def init_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("To-Do List Manager")
        self.setMinimumSize(600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        title = QLabel("TASK MANAGER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.Box)
        input_layout = QHBoxLayout(input_frame)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task...")
        input_layout.addWidget(self.task_input)
        
        date_label = QLabel("Due:")
        input_layout.addWidget(date_label)
        
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate().addDays(7))
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("yyyy-MM-dd")
        input_layout.addWidget(self.date_picker)
        
        self.add_button = QPushButton("+ Add Task")
        self.add_button.setFixedWidth(100)
        self.add_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.add_button)
        
        main_layout.addWidget(input_frame)
        
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        main_layout.addWidget(self.task_list)
        
        button_layout = QHBoxLayout()
        
        self.complete_button = QPushButton("Mark Complete")
        self.complete_button.clicked.connect(self.mark_complete)
        button_layout.addWidget(self.complete_button)
        
        self.delete_button = QPushButton("Delete Task")
        self.delete_button.clicked.connect(self.delete_task)
        button_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_list)
        button_layout.addWidget(self.refresh_button)
        
        self.filter_all = QPushButton("All")
        self.filter_all.clicked.connect(lambda: self.refresh_list("all"))
        button_layout.addWidget(self.filter_all)
        
        self.filter_active = QPushButton("Active")
        self.filter_active.clicked.connect(lambda: self.refresh_list("active"))
        button_layout.addWidget(self.filter_active)
        
        self.filter_completed = QPushButton("Completed")
        self.filter_completed.clicked.connect(lambda: self.refresh_list("completed"))
        button_layout.addWidget(self.filter_completed)
        
        main_layout.addLayout(button_layout)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.current_filter = "all"
        self.refresh_list()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r") as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task) for task in data]
            except:
                self.tasks = []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(TASKS_FILE, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2)
    
    def add_task(self):
        """Add a new task"""
        description = self.task_input.text().strip()
        if not description:
            QMessageBox.warning(self, "Warning", "Please enter a task description!")
            return
        
        due_date = self.date_picker.date().toString("yyyy-MM-dd")
        
        new_task = Task(description, due_date)
        self.tasks.append(new_task)
        self.save_tasks()
        
        self.task_input.clear()
        self.date_picker.setDate(QDate.currentDate().addDays(7))
        
        self.refresh_list()
        self.status_bar.showMessage("Task added successfully!", 3000)
    
    def mark_complete(self):
        """Mark selected task as complete"""
        current_item = self.task_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a task to mark as complete!")
            return
        
        task_index = current_item.data(Qt.ItemDataRole.UserRole)
        if task_index is not None and 0 <= task_index < len(self.tasks):
            task = self.tasks[task_index]
            if not task.completed:
                task.completed = True
                self.save_tasks()
                self.refresh_list()
                self.status_bar.showMessage("Task marked as complete!", 3000)
            else:
                QMessageBox.information(self, "Info", "Task is already completed!")
    
    def delete_task(self):
        """Delete selected task"""
        current_item = self.task_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a task to delete!")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this task?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            task_index = current_item.data(Qt.ItemDataRole.UserRole)
            if task_index is not None:
                deleted_task = self.tasks.pop(task_index)
                self.save_tasks()
                self.refresh_list()
                self.status_bar.showMessage("Deleted: " + deleted_task.description, 3000)
    
    def refresh_list(self, filter_type=None):
        """Refresh the task list display"""
        if filter_type:
            self.current_filter = filter_type
        
        self.task_list.clear()
        
        if self.current_filter == "active":
            filtered_tasks = [t for t in self.tasks if not t.completed]
        elif self.current_filter == "completed":
            filtered_tasks = [t for t in self.tasks if t.completed]
        else:  # "all"
            filtered_tasks = self.tasks
        
        if not filtered_tasks:
            empty_item = QListWidgetItem("[ No tasks found ]")
            empty_item.setForeground(Qt.GlobalColor.gray)
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_list.addItem(empty_item)
            self.status_bar.showMessage("No tasks to display", 2000)
            return
        
        for i, task in enumerate(filtered_tasks):
            status = "[X]" if task.completed else "[ ]"
            
            is_overdue = False
            if not task.completed and task.due_date:
                try:
                    due_date = datetime.strptime(task.due_date, "%Y-%m-%d")
                    if due_date < datetime.now():
                        is_overdue = True
                except:
                    pass
            
            due_text = ""
            if task.due_date:
                due_text = f" [Due: {task.due_date}]"
                if is_overdue:
                    due_text = f" [OVERDUE: {task.due_date}]"
            
            display_text = f"{status} {task.description}{due_text}"
            
            item = QListWidgetItem(display_text)
            
            if task.completed:
                item.setForeground(Qt.GlobalColor.darkGray)
            elif is_overdue:
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setForeground(Qt.GlobalColor.black)
            
            original_index = self.tasks.index(task)
            item.setData(Qt.ItemDataRole.UserRole, original_index)
            
            tooltip = f"Created: {task.created}\n"
            if task.due_date:
                tooltip += f"Due: {task.due_date}\n"
            tooltip += f"Status: {'Completed' if task.completed else 'Active'}"
            item.setToolTip(tooltip)
            
            self.task_list.addItem(item)
        
        active_count = sum(1 for t in self.tasks if not t.completed)
        completed_count = sum(1 for t in self.tasks if t.completed)
        self.status_bar.showMessage(
            f"Total: {len(self.tasks)} | Active: {active_count} | Completed: {completed_count}",
            5000
        )

def main():
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    window = ToDoApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()