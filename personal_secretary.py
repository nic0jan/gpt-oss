#!/usr/bin/env python3
"""
Personal Secretary using GPT-OSS
A comprehensive life aid for agenda management, task followup, and project planning.
"""

import json
import datetime
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    status: Status
    due_date: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    project_id: Optional[str] = None
    tags: List[str] = None
    estimated_duration: Optional[int] = None  # in minutes
    actual_duration: Optional[int] = None
    dependencies: List[str] = None  # task IDs this task depends on
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class Project:
    id: str
    name: str
    description: str
    status: Status
    start_date: Optional[datetime.datetime]
    end_date: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    milestones: List[Dict[str, Any]] = None
    tags: List[str] = None
    progress_percentage: float = 0.0
    
    def __post_init__(self):
        if self.milestones is None:
            self.milestones = []
        if self.tags is None:
            self.tags = []

@dataclass
class CalendarEvent:
    id: str
    title: str
    description: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    location: Optional[str] = None
    attendees: List[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    reminder_minutes: List[int] = None  # minutes before event
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.reminder_minutes is None:
            self.reminder_minutes = [15, 60]  # default reminders

class PersonalSecretaryDatabase:
    """Database manager for personal secretary data"""
    
    def __init__(self, db_path: str = "personal_secretary.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                project_id TEXT,
                tags TEXT,  -- JSON array
                estimated_duration INTEGER,
                actual_duration INTEGER,
                dependencies TEXT  -- JSON array
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                milestones TEXT,  -- JSON array
                tags TEXT,  -- JSON array
                progress_percentage REAL DEFAULT 0.0
            )
        ''')
        
        # Calendar events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                attendees TEXT,  -- JSON array
                is_recurring BOOLEAN DEFAULT FALSE,
                recurrence_pattern TEXT,
                reminder_minutes TEXT  -- JSON array
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_task(self, task: Task):
        """Save a task to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (id, title, description, priority, status, due_date, created_at, updated_at,
             project_id, tags, estimated_duration, actual_duration, dependencies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.title, task.description, task.priority.value, task.status.value,
            task.due_date.isoformat() if task.due_date else None,
            task.created_at.isoformat(), task.updated_at.isoformat(),
            task.project_id, json.dumps(task.tags), task.estimated_duration,
            task.actual_duration, json.dumps(task.dependencies)
        ))
        
        conn.commit()
        conn.close()
    
    def get_tasks(self, status: Optional[Status] = None, project_id: Optional[str] = None) -> List[Task]:
        """Retrieve tasks from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        query += " ORDER BY due_date ASC, priority DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            task = Task(
                id=row[0], title=row[1], description=row[2],
                priority=Priority(row[3]), status=Status(row[4]),
                due_date=datetime.datetime.fromisoformat(row[5]) if row[5] else None,
                created_at=datetime.datetime.fromisoformat(row[6]),
                updated_at=datetime.datetime.fromisoformat(row[7]),
                project_id=row[8], tags=json.loads(row[9]) if row[9] else [],
                estimated_duration=row[10], actual_duration=row[11],
                dependencies=json.loads(row[12]) if row[12] else []
            )
            tasks.append(task)
        
        conn.close()
        return tasks
    
    def save_project(self, project: Project):
        """Save a project to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO projects 
            (id, name, description, status, start_date, end_date, created_at, updated_at,
             milestones, tags, progress_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project.id, project.name, project.description, project.status.value,
            project.start_date.isoformat() if project.start_date else None,
            project.end_date.isoformat() if project.end_date else None,
            project.created_at.isoformat(), project.updated_at.isoformat(),
            json.dumps(project.milestones), json.dumps(project.tags),
            project.progress_percentage
        ))
        
        conn.commit()
        conn.close()
    
    def get_projects(self, status: Optional[Status] = None) -> List[Project]:
        """Retrieve projects from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM projects WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        projects = []
        for row in rows:
            project = Project(
                id=row[0], name=row[1], description=row[2], status=Status(row[3]),
                start_date=datetime.datetime.fromisoformat(row[4]) if row[4] else None,
                end_date=datetime.datetime.fromisoformat(row[5]) if row[5] else None,
                created_at=datetime.datetime.fromisoformat(row[6]),
                updated_at=datetime.datetime.fromisoformat(row[7]),
                milestones=json.loads(row[8]) if row[8] else [],
                tags=json.loads(row[9]) if row[9] else [],
                progress_percentage=row[10]
            )
            projects.append(project)
        
        conn.close()
        return projects

class PersonalSecretaryTools:
    """Custom tools for personal secretary functionality"""
    
    def __init__(self, db: PersonalSecretaryDatabase):
        self.db = db
    
    def create_task(self, title: str, description: str = "", priority: str = "medium",
                   due_date: Optional[str] = None, project_id: Optional[str] = None,
                   tags: List[str] = None, estimated_duration: Optional[int] = None) -> Dict[str, Any]:
        """Create a new task"""
        task_id = f"task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.datetime.now()
        
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.datetime.fromisoformat(due_date)
            except ValueError:
                return {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=Priority(priority.lower()),
            status=Status.TODO,
            due_date=due_datetime,
            created_at=now,
            updated_at=now,
            project_id=project_id,
            tags=tags or [],
            estimated_duration=estimated_duration
        )
        
        self.db.save_task(task)
        return {"success": True, "task_id": task_id, "message": f"Task '{title}' created successfully"}
    
    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """Update task status"""
        tasks = self.db.get_tasks()
        task = next((t for t in tasks if t.id == task_id), None)
        
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        try:
            task.status = Status(status.lower())
            task.updated_at = datetime.datetime.now()
            self.db.save_task(task)
            return {"success": True, "message": f"Task status updated to {status}"}
        except ValueError:
            return {"error": f"Invalid status. Valid options: {[s.value for s in Status]}"}
    
    def create_project(self, name: str, description: str = "", start_date: Optional[str] = None,
                      end_date: Optional[str] = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new project"""
        project_id = f"project_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.datetime.now()
        
        start_datetime = None
        if start_date:
            try:
                start_datetime = datetime.datetime.fromisoformat(start_date)
            except ValueError:
                return {"error": "Invalid start date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
        
        end_datetime = None
        if end_date:
            try:
                end_datetime = datetime.datetime.fromisoformat(end_date)
            except ValueError:
                return {"error": "Invalid end date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
        
        project = Project(
            id=project_id,
            name=name,
            description=description,
            status=Status.TODO,
            start_date=start_datetime,
            end_date=end_datetime,
            created_at=now,
            updated_at=now,
            tags=tags or []
        )
        
        self.db.save_project(project)
        return {"success": True, "project_id": project_id, "message": f"Project '{name}' created successfully"}
    
    def add_milestone(self, project_id: str, milestone_name: str, target_date: str,
                     description: str = "") -> Dict[str, Any]:
        """Add a milestone to a project"""
        projects = self.db.get_projects()
        project = next((p for p in projects if p.id == project_id), None)
        
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        try:
            target_datetime = datetime.datetime.fromisoformat(target_date)
        except ValueError:
            return {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
        
        milestone = {
            "name": milestone_name,
            "description": description,
            "target_date": target_date,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        project.milestones.append(milestone)
        project.updated_at = datetime.datetime.now()
        self.db.save_project(project)
        
        return {"success": True, "message": f"Milestone '{milestone_name}' added to project"}
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get a summary of today's tasks and events"""
        today = datetime.datetime.now().date()
        tasks = self.db.get_tasks()
        
        today_tasks = [t for t in tasks if t.due_date and t.due_date.date() == today]
        overdue_tasks = [t for t in tasks if t.due_date and t.due_date.date() < today and t.status != Status.COMPLETED]
        high_priority_tasks = [t for t in tasks if t.priority in [Priority.HIGH, Priority.URGENT] and t.status != Status.COMPLETED]
        
        return {
            "date": today.isoformat(),
            "today_tasks": len(today_tasks),
            "overdue_tasks": len(overdue_tasks),
            "high_priority_tasks": len(high_priority_tasks),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority.value,
                    "status": t.status.value,
                    "due_date": t.due_date.isoformat() if t.due_date else None
                }
                for t in today_tasks + overdue_tasks + high_priority_tasks
            ]
        }
    
    def suggest_next_actions(self) -> Dict[str, Any]:
        """Suggest next actions based on current tasks and priorities"""
        tasks = self.db.get_tasks(status=Status.TODO)
        projects = self.db.get_projects(status=Status.IN_PROGRESS)
        
        suggestions = []
        
        # Suggest urgent tasks
        urgent_tasks = [t for t in tasks if t.priority == Priority.URGENT]
        if urgent_tasks:
            suggestions.append({
                "type": "urgent_task",
                "message": f"You have {len(urgent_tasks)} urgent task(s) that need immediate attention",
                "tasks": [{"id": t.id, "title": t.title} for t in urgent_tasks[:3]]
            })
        
        # Suggest overdue tasks
        overdue_tasks = [t for t in tasks if t.due_date and t.due_date.date() < datetime.datetime.now().date()]
        if overdue_tasks:
            suggestions.append({
                "type": "overdue_task",
                "message": f"You have {len(overdue_tasks)} overdue task(s)",
                "tasks": [{"id": t.id, "title": t.title, "days_overdue": (datetime.datetime.now().date() - t.due_date.date()).days} for t in overdue_tasks[:3]]
            })
        
        # Suggest project milestones
        upcoming_milestones = []
        for project in projects:
            for milestone in project.milestones:
                if milestone["status"] == "pending":
                    target_date = datetime.datetime.fromisoformat(milestone["target_date"])
                    days_until = (target_date.date() - datetime.datetime.now().date()).days
                    if 0 <= days_until <= 7:  # Within a week
                        upcoming_milestones.append({
                            "project": project.name,
                            "milestone": milestone["name"],
                            "days_until": days_until
                        })
        
        if upcoming_milestones:
            suggestions.append({
                "type": "upcoming_milestone",
                "message": f"You have {len(upcoming_milestones)} milestone(s) due within a week",
                "milestones": upcoming_milestones[:3]
            })
        
        return {"suggestions": suggestions}

def main():
    """Main function to demonstrate the personal secretary"""
    print("🤖 Personal Secretary using GPT-OSS")
    print("=" * 50)
    
    # Initialize database and tools
    db = PersonalSecretaryDatabase()
    tools = PersonalSecretaryTools(db)
    
    # Example usage
    print("\n📝 Creating sample tasks...")
    tools.create_task("Review quarterly reports", "Analyze Q4 performance metrics", "high", 
                     "2024-01-15T17:00:00", tags=["work", "reports"])
    tools.create_task("Grocery shopping", "Buy ingredients for weekend cooking", "medium",
                     "2024-01-12T18:00:00", tags=["personal", "shopping"])
    
    print("\n📋 Creating sample project...")
    tools.create_project("Website Redesign", "Complete redesign of company website",
                        "2024-01-10T09:00:00", "2024-03-31T17:00:00", ["work", "web"])
    
    print("\n📊 Daily Summary:")
    summary = tools.get_daily_summary()
    print(f"Today's tasks: {summary['today_tasks']}")
    print(f"Overdue tasks: {summary['overdue_tasks']}")
    print(f"High priority tasks: {summary['high_priority_tasks']}")
    
    print("\n💡 Suggestions:")
    suggestions = tools.suggest_next_actions()
    for suggestion in suggestions["suggestions"]:
        print(f"- {suggestion['message']}")

if __name__ == "__main__":
    main()