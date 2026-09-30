import uuid
from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

class Task:
    def __init__(self, task_id, name, description, due_date):
        self.task_id = task_id  # User-provided task ID
        self.name = name
        self.description = description
        self.due_date = due_date
        self.assigned_to = None  # Initially unassigned

class Project:
    def __init__(self, project_id, name):
        self.project_id = project_id  # Use short or custom project ID
        self.name = name
        self.tasks = []  # List to store tasks

class TeamMember:
    def __init__(self, team_member_id, name):
        self.team_member_id = team_member_id  # User-provided team member ID
        self.name = name

class ProjectManagementTool:
    def __init__(self):
        self.projects = {}
        self.tasks = {}
        self.team_members = {}
        self.load_data()

    def create_project(self, name, project_id):
        if project_id in self.projects:
            messagebox.showerror("Error", f"Project ID {project_id} already exists.")
            return None
        project = Project(project_id, name)
        self.projects[project.project_id] = project
        self.save_data()
        messagebox.showinfo("Success", f"Project '{name}' created successfully!")
        return project.project_id

    def create_task(self, project_id, task_id, name, description, due_date):
        if project_id not in self.projects:
            messagebox.showerror("Error", f"Project ID {project_id} not found.")
            return
        if task_id in self.tasks:
            messagebox.showerror("Error", f"Task ID {task_id} already exists.")
            return
        task = Task(task_id, name, description, due_date)
        self.tasks[task.task_id] = task
        self.projects[project_id].tasks.append(task)
        self.save_data()
        messagebox.showinfo("Success", f"Task '{name}' created successfully!")
        return task.task_id

    def create_team_member(self, team_member_id, name):
        if team_member_id in self.team_members:
            messagebox.showerror("Error", f"Team member ID {team_member_id} already exists.")
            return
        team_member = TeamMember(team_member_id, name)
        self.team_members[team_member.team_member_id] = team_member
        self.save_data()
        messagebox.showinfo("Success", f"Team member '{name}' created successfully!")
        return team_member.team_member_id

    def assign_task(self, task_id, team_member_id):
        task = self.tasks.get(task_id)
        if task:
            team_member = self.team_members.get(team_member_id)
            if team_member:
                task.assigned_to = team_member
                self.save_data()
                messagebox.showinfo("Success", f"Task '{task.name}' assigned to '{team_member.name}' successfully!")
            else:
                messagebox.showerror("Error", f"Team member with ID {team_member_id} not found.")
        else:
            messagebox.showerror("Error", f"Task with ID {task_id} not found.")

    def generate_project_timeline(self, project_id):
        project = self.projects.get(project_id)
        if project:
            timeline = f"Project Timeline for {project.name}:\n"
            for task in project.tasks:
                assigned_to = task.assigned_to.name if task.assigned_to else 'Unassigned'
                timeline += f"- {task.name} (Due: {task.due_date}) - Assigned to: {assigned_to}\n"
            messagebox.showinfo("Project Timeline", timeline)
        else:
            messagebox.showerror("Error", f"Project with ID {project_id} not found.")

    def view_all_projects_and_tasks(self):
        if not self.projects:
            messagebox.showinfo("Info", "No projects available.")
            return

        all_projects = ""
        for project_id, project in self.projects.items():
            all_projects += f"\nProject: {project.name} (ID: {project_id})\n"
            if not project.tasks:
                all_projects += "  No tasks in this project.\n"
            for task in project.tasks:
                assigned_to = task.assigned_to.name if task.assigned_to else 'Unassigned'
                all_projects += f"  - Task: {task.name} (ID: {task.task_id})\n"
                all_projects += f"    Description: {task.description}\n"
                all_projects += f"    Due Date: {task.due_date}\n"
                all_projects += f"    Assigned to: {assigned_to}\n"

        messagebox.showinfo("All Projects and Tasks", all_projects)

    # Saving and loading data for persistence
    def save_data(self):
        data = {
            'projects': {
                project_id: {
                    'project_id': project.project_id,
                    'name': project.name,
                    'tasks': [
                        {
                            'task_id': task.task_id,
                            'name': task.name,
                            'description': task.description,
                            'due_date': task.due_date.strftime("%Y-%m-%d"),  # Convert datetime to string
                            'assigned_to': task.assigned_to.team_member_id if task.assigned_to else None
                        }
                        for task in project.tasks
                    ]
                }
                for project_id, project in self.projects.items()
            },
            'team_members': {
                team_member_id: {
                    'team_member_id': member.team_member_id,
                    'name': member.name
                }
                for team_member_id, member in self.team_members.items()
            }
        }

        with open('project_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists('project_data.json'):
            with open('project_data.json', 'r') as f:
                data = json.load(f)
                # Reload data into objects (simplified)
                for proj_id, proj_data in data.get('projects', {}).items():
                    project = Project(proj_data['project_id'], proj_data['name'])
                    for task_data in proj_data['tasks']:
                        task = Task(
                            task_data['task_id'],  # Use provided task ID
                            task_data['name'],
                            task_data['description'],
                            datetime.strptime(task_data['due_date'], "%Y-%m-%d")  # Convert string back to datetime
                        )
                        task.assigned_to = self.team_members.get(task_data['assigned_to']) if task_data['assigned_to'] else None
                        project.tasks.append(task)
                    self.projects[proj_id] = project
                for member_id, member_data in data.get('team_members', {}).items():
                    member = TeamMember(member_id, member_data['name'])  # Use provided team member ID
                    self.team_members[member_id] = member

class ProjectManagementGUI:
    def __init__(self, master):
        self.master = master
        master.title("Project Management System")
        master.geometry("400x400")

        # Heading
        self.heading = tk.Label(master, text="Project Management System", font=("Helvetica", 16, "bold"))
        self.heading.pack(pady=10)

        # Initialize ProjectManagementTool
        self.tool = ProjectManagementTool()

        # Buttons for functionalities
        self.create_project_button = tk.Button(master, text="Create Project", command=self.create_project)
        self.create_project_button.pack(pady=5)

        self.create_task_button = tk.Button(master, text="Create Task", command=self.create_task)
        self.create_task_button.pack(pady=5)

        self.create_team_member_button = tk.Button(master, text="Create Team Member", command=self.create_team_member)
        self.create_team_member_button.pack(pady=5)

        self.assign_task_button = tk.Button(master, text="Assign Task", command=self.assign_task)
        self.assign_task_button.pack(pady=5)

        self.view_project_timeline_button = tk.Button(master, text="View Project Timeline", command=self.view_project_timeline)
        self.view_project_timeline_button.pack(pady=5)

        self.view_all_button = tk.Button(master, text="View All Projects and Tasks", command=self.view_all_projects_and_tasks)
        self.view_all_button.pack(pady=5)

    def create_project(self):
        project_name = simpledialog.askstring("Project Name", "Enter project name:")
        project_id = simpledialog.askstring("Project ID", "Enter project ID:")
        if project_name and project_id:
            self.tool.create_project(project_name, project_id)

    def create_task(self):
        project_id = simpledialog.askstring("Project ID", "Enter project ID:")
        task_id = simpledialog.askstring("Task ID", "Enter task ID:")
        task_name = simpledialog.askstring("Task Name", "Enter task name:")
        task_description = simpledialog.askstring("Task Description", "Enter task description:")
        due_date_input = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
        if project_id and task_id and task_name and task_description and due_date_input:
            try:
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Setting default due date to 2024-12-31.")
                due_date = datetime(2024, 12, 31)
            self.tool.create_task(project_id, task_id, task_name, task_description, due_date)

    def create_team_member(self):
        team_member_id = simpledialog.askstring("Team Member ID", "Enter team member ID:")
        team_member_name = simpledialog.askstring("Team Member Name", "Enter team member name:")
        if team_member_id and team_member_name:
            self.tool.create_team_member(team_member_id, team_member_name)

    def assign_task(self):
        task_id = simpledialog.askstring("Task ID", "Enter task ID:")
        team_member_id = simpledialog.askstring("Team Member ID", "Enter team member ID:")
        if task_id and team_member_id:
            self.tool.assign_task(task_id, team_member_id)

    def view_project_timeline(self):
        project_id = simpledialog.askstring("Project ID", "Enter project ID:")
        if project_id:
            self.tool.generate_project_timeline(project_id)

    def view_all_projects_and_tasks(self):
        self.tool.view_all_projects_and_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagementGUI(root)
    root.mainloop()