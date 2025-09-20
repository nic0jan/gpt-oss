#!/usr/bin/env python3
"""
Personal Secretary Web Interface
A Streamlit-based web interface for the GPT-OSS Personal Secretary
"""

import streamlit as st
import asyncio
import json
import datetime
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_chat import message

from gpt_oss_personal_secretary import GPTOSSPersonalSecretary
from personal_secretary import PersonalSecretaryDatabase, PersonalSecretaryTools, Priority, Status

# Configure Streamlit page
st.set_page_config(
    page_title="GPT-OSS Personal Secretary",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .task-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 0.5rem;
    }
    .priority-urgent { border-left: 4px solid #ff4444; }
    .priority-high { border-left: 4px solid #ff8800; }
    .priority-medium { border-left: 4px solid #ffbb00; }
    .priority-low { border-left: 4px solid #44ff44; }
</style>
""", unsafe_allow_html=True)

class PersonalSecretaryUI:
    """Streamlit UI for Personal Secretary"""
    
    def __init__(self):
        self.secretary = GPTOSSPersonalSecretary()
        self.db = PersonalSecretaryDatabase()
        self.tools = PersonalSecretaryTools(self.db)
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
    
    def render_header(self):
        """Render the main header"""
        st.markdown('<h1 class="main-header">🤖 GPT-OSS Personal Secretary</h1>', unsafe_allow_html=True)
        st.markdown("Your intelligent life management assistant powered by GPT-OSS")
    
    def render_sidebar(self):
        """Render the sidebar with navigation and quick actions"""
        st.sidebar.title("📋 Quick Actions")
        
        # Quick task creation
        with st.sidebar.expander("➕ Quick Add Task", expanded=False):
            with st.form("quick_task_form"):
                title = st.text_input("Task Title")
                priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
                due_date = st.date_input("Due Date", value=datetime.date.today())
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Add Task"):
                        if title:
                            result = self.tools.create_task(
                                title=title,
                                priority=priority,
                                due_date=due_date.isoformat()
                            )
                            if result.get("success"):
                                st.success(f"Task '{title}' created!")
                                st.rerun()
                            else:
                                st.error(result.get("error", "Failed to create task"))
        
        # Quick project creation
        with st.sidebar.expander("📁 Quick Add Project", expanded=False):
            with st.form("quick_project_form"):
                name = st.text_input("Project Name")
                description = st.text_area("Description")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Add Project"):
                        if name:
                            result = self.tools.create_project(name=name, description=description)
                            if result.get("success"):
                                st.success(f"Project '{name}' created!")
                                st.rerun()
                            else:
                                st.error(result.get("error", "Failed to create project"))
        
        # Navigation
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📊 Navigation")
        
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Dashboard", "Tasks", "Projects", "Chat Assistant", "Analytics"]
        )
        
        return page
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.header("📊 Dashboard")
        
        # Get summary data
        summary = self.tools.get_daily_summary()
        suggestions = self.tools.suggest_next_actions()
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Today's Tasks",
                value=summary['today_tasks'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="Overdue Tasks",
                value=summary['overdue_tasks'],
                delta=None
            )
        
        with col3:
            st.metric(
                label="High Priority",
                value=summary['high_priority_tasks'],
                delta=None
            )
        
        with col4:
            projects = self.db.get_projects(status=Status.IN_PROGRESS)
            st.metric(
                label="Active Projects",
                value=len(projects),
                delta=None
            )
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Today's Focus")
            
            # Display tasks
            tasks = self.db.get_tasks()
            today_tasks = [t for t in tasks if t.due_date and t.due_date.date() == datetime.date.today()]
            urgent_tasks = [t for t in tasks if t.priority == Priority.URGENT and t.status != Status.COMPLETED]
            
            all_focus_tasks = today_tasks + urgent_tasks
            
            if all_focus_tasks:
                for task in all_focus_tasks[:5]:  # Show top 5
                    priority_class = f"priority-{task.priority.value}"
                    with st.container():
                        st.markdown(f"""
                        <div class="task-card {priority_class}">
                            <strong>{task.title}</strong><br>
                            <small>Priority: {task.priority.value.title()} | Status: {task.status.value.title()}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No tasks scheduled for today. Great job!")
        
        with col2:
            st.subheader("💡 Suggestions")
            
            if suggestions['suggestions']:
                for suggestion in suggestions['suggestions'][:3]:
                    st.info(suggestion['message'])
            else:
                st.success("No urgent actions needed!")
        
        # Weekly overview
        st.subheader("📅 Weekly Overview")
        
        # Create a simple weekly chart
        week_data = []
        for i in range(7):
            date = datetime.date.today() - datetime.timedelta(days=6-i)
            tasks_on_date = [t for t in tasks if t.due_date and t.due_date.date() == date]
            week_data.append({
                'Date': date.strftime('%A'),
                'Tasks': len(tasks_on_date),
                'Completed': len([t for t in tasks_on_date if t.status == Status.COMPLETED])
            })
        
        if week_data:
            df_week = pd.DataFrame(week_data)
            fig = px.bar(df_week, x='Date', y=['Tasks', 'Completed'], 
                       title="Tasks by Day", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    def render_tasks_page(self):
        """Render the tasks management page"""
        st.header("📝 Task Management")
        
        # Task filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Todo", "In Progress", "Completed", "Cancelled"]
            )
        
        with col2:
            priority_filter = st.selectbox(
                "Filter by Priority",
                ["All", "Low", "Medium", "High", "Urgent"]
            )
        
        with col3:
            project_filter = st.selectbox(
                "Filter by Project",
                ["All"] + [p.name for p in self.db.get_projects()]
            )
        
        # Get filtered tasks
        tasks = self.db.get_tasks()
        
        if status_filter != "All":
            tasks = [t for t in tasks if t.status.value == status_filter.lower().replace(" ", "_")]
        
        if priority_filter != "All":
            tasks = [t for t in tasks if t.priority.value == priority_filter.lower()]
        
        if project_filter != "All":
            project_id = next((p.id for p in self.db.get_projects() if p.name == project_filter), None)
            if project_id:
                tasks = [t for t in tasks if t.project_id == project_id]
        
        # Display tasks
        if tasks:
            for task in tasks:
                priority_class = f"priority-{task.priority.value}"
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="task-card {priority_class}">
                        <strong>{task.title}</strong><br>
                        <small>{task.description}</small><br>
                        <small>Due: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'No due date'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    new_status = st.selectbox(
                        f"Status {task.id}",
                        ["todo", "in_progress", "completed", "cancelled"],
                        index=list(Status).index(task.status),
                        key=f"status_{task.id}"
                    )
                    if new_status != task.status.value:
                        self.tools.update_task_status(task.id, new_status)
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_{task.id}"):
                        # Add delete functionality
                        st.info("Delete functionality would be implemented here")
        else:
            st.info("No tasks found with the current filters.")
    
    def render_projects_page(self):
        """Render the projects management page"""
        st.header("📁 Project Management")
        
        projects = self.db.get_projects()
        
        if projects:
            for project in projects:
                with st.expander(f"📁 {project.name} - {project.status.value.title()}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {project.description}")
                        st.write(f"**Progress:** {project.progress_percentage:.1f}%")
                        
                        if project.start_date:
                            st.write(f"**Start Date:** {project.start_date.strftime('%Y-%m-%d')}")
                        if project.end_date:
                            st.write(f"**End Date:** {project.end_date.strftime('%Y-%m-%d')}")
                        
                        if project.tags:
                            st.write(f"**Tags:** {', '.join(project.tags)}")
                    
                    with col2:
                        # Progress bar
                        st.progress(project.progress_percentage / 100)
                        
                        # Milestones
                        if project.milestones:
                            st.write("**Milestones:**")
                            for milestone in project.milestones:
                                status_emoji = "✅" if milestone["status"] == "completed" else "⏳"
                                st.write(f"{status_emoji} {milestone['name']}")
        
        # Add new milestone form
        st.subheader("➕ Add Milestone")
        with st.form("add_milestone_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.selectbox("Project", [p.name for p in projects])
                milestone_name = st.text_input("Milestone Name")
            
            with col2:
                target_date = st.date_input("Target Date")
                description = st.text_area("Description")
            
            if st.form_submit_button("Add Milestone"):
                project_id = next((p.id for p in projects if p.name == project_name), None)
                if project_id and milestone_name:
                    result = self.tools.add_milestone(
                        project_id=project_id,
                        milestone_name=milestone_name,
                        target_date=target_date.isoformat(),
                        description=description
                    )
                    if result.get("success"):
                        st.success(f"Milestone '{milestone_name}' added!")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Failed to add milestone"))
    
    def render_chat_page(self):
        """Render the chat interface"""
        st.header("💬 Chat with Your Personal Secretary")
        
        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask your personal secretary anything..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = asyncio.run(self.secretary.chat(prompt))
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    def render_analytics_page(self):
        """Render the analytics page"""
        st.header("📈 Analytics & Insights")
        
        # Get data
        tasks = self.db.get_tasks()
        projects = self.db.get_projects()
        
        # Productivity analysis
        analysis = asyncio.run(self.secretary.personal_secretary_tool._analyze_productivity())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Task Completion")
            
            completed_tasks = [t for t in tasks if t.status == Status.COMPLETED]
            total_tasks = len(tasks)
            completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0
            
            st.metric("Completion Rate", f"{completion_rate:.1%}")
            
            # Priority distribution pie chart
            priority_counts = {}
            for task in tasks:
                if task.status != Status.COMPLETED:
                    priority_counts[task.priority.value] = priority_counts.get(task.priority.value, 0) + 1
            
            if priority_counts:
                fig_pie = px.pie(
                    values=list(priority_counts.values()),
                    names=list(priority_counts.keys()),
                    title="Active Tasks by Priority"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("📅 Task Timeline")
            
            # Tasks over time
            task_dates = []
            for task in tasks:
                if task.created_at:
                    task_dates.append({
                        'Date': task.created_at.date(),
                        'Tasks': 1,
                        'Status': task.status.value
                    })
            
            if task_dates:
                df_timeline = pd.DataFrame(task_dates)
                df_grouped = df_timeline.groupby(['Date', 'Status']).size().reset_index(name='Count')
                
                fig_timeline = px.bar(
                    df_grouped,
                    x='Date',
                    y='Count',
                    color='Status',
                    title="Tasks Created Over Time"
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Project progress
        st.subheader("📁 Project Progress")
        
        if projects:
            project_data = []
            for project in projects:
                project_data.append({
                    'Project': project.name,
                    'Progress': project.progress_percentage,
                    'Status': project.status.value
                })
            
            df_projects = pd.DataFrame(project_data)
            fig_projects = px.bar(
                df_projects,
                x='Project',
                y='Progress',
                color='Status',
                title="Project Progress"
            )
            st.plotly_chart(fig_projects, use_container_width=True)
    
    def run(self):
        """Main run method"""
        self.render_header()
        
        # Sidebar navigation
        page = self.render_sidebar()
        
        # Main content based on selected page
        if page == "Dashboard":
            self.render_dashboard()
        elif page == "Tasks":
            self.render_tasks_page()
        elif page == "Projects":
            self.render_projects_page()
        elif page == "Chat Assistant":
            self.render_chat_page()
        elif page == "Analytics":
            self.render_analytics_page()

def main():
    """Main function to run the Streamlit app"""
    ui = PersonalSecretaryUI()
    ui.run()

if __name__ == "__main__":
    main()