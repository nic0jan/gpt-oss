# GPT-OSS Personal Secretary: Complete Life Management System

## 🎯 Overview

Your **GPT-OSS Personal Secretary** is a comprehensive AI-powered life management system that combines the intelligence of OpenAI's GPT-OSS models with practical tools for managing your daily life, projects, and long-term goals.

## 🚀 Quick Start

### 1. Installation
```bash
# Run the setup script
python3 setup_personal_secretary.py

# Start the application
./start_personal_secretary.sh
```

### 2. Access the Interface
Open your browser and navigate to: **http://localhost:8501**

## 🎨 Interface Overview

### 📊 Dashboard
- **Daily metrics**: Tasks due today, overdue items, high priority tasks
- **Focus area**: Today's most important tasks
- **Smart suggestions**: AI-powered recommendations
- **Weekly overview**: Visual representation of your week

### 📝 Task Management
- **Create tasks** with priorities, due dates, and project associations
- **Filter and organize** by status, priority, or project
- **Update status** with simple dropdowns
- **Track progress** with visual indicators

### 📁 Project Management
- **Create projects** with milestones and deadlines
- **Track progress** with percentage completion
- **Manage milestones** with target dates
- **Associate tasks** with specific projects

### 💬 Chat Assistant
- **Natural language** interaction with your AI secretary
- **Intelligent responses** based on your data
- **Proactive suggestions** for next actions
- **Context-aware** recommendations

### 📈 Analytics
- **Productivity analysis** with completion rates
- **Priority distribution** charts
- **Timeline visualization** of task creation
- **Project progress** tracking

## 🛠️ Core Features

### 1. Task Management
```python
# Create a task
tools.create_task(
    title="Review quarterly reports",
    description="Analyze Q4 performance metrics",
    priority="high",
    due_date="2024-01-15T17:00:00",
    project_id="project_123",
    tags=["work", "reports"],
    estimated_duration=120  # minutes
)

# Update task status
tools.update_task_status("task_123", "completed")

# Get tasks with filters
tasks = db.get_tasks(status=Status.IN_PROGRESS, project_id="project_123")
```

### 2. Project Planning
```python
# Create a project
tools.create_project(
    name="Website Redesign",
    description="Complete redesign with modern UI/UX",
    start_date="2024-01-10T09:00:00",
    end_date="2024-03-31T17:00:00",
    tags=["work", "web", "design"]
)

# Add milestones
tools.add_milestone(
    project_id="project_123",
    milestone_name="Design Phase Complete",
    target_date="2024-02-15T17:00:00",
    description="All mockups and design system ready"
)
```

### 3. Intelligent Analysis
```python
# Get daily summary
summary = tools.get_daily_summary()
# Returns: today's tasks, overdue items, high priority tasks

# Get suggestions
suggestions = tools.suggest_next_actions()
# Returns: AI-powered recommendations based on current state

# Analyze productivity
analysis = secretary.analyze_productivity()
# Returns: completion rates, time analysis, priority distribution
```

## 💬 Chat Commands

### Task Management
- **"Create a task: Review quarterly reports, high priority, due tomorrow"**
- **"Show me today's tasks"**
- **"What tasks are overdue?"**
- **"Update task status to completed"**

### Project Management
- **"Create a project: Learn Spanish, 3 months duration"**
- **"Add milestone: Complete beginner course by next Friday"**
- **"Show project progress"**
- **"What milestones are coming up?"**

### Planning & Analysis
- **"What should I focus on next?"**
- **"Analyze my productivity"**
- **"Help me plan this week"**
- **"Show me my daily summary"**

### General Assistance
- **"What's my schedule for today?"**
- **"How am I doing with my goals?"**
- **"Suggest ways to improve productivity"**
- **"Create a morning routine"**

## 🔧 Configuration

### Database Settings
```ini
[DATABASE]
db_path = "data/personal_secretary.db"
```

### GPT-OSS Settings
```ini
[GPT_OSS]
model_name = "gpt-oss-20b"  # or "gpt-oss-120b"
reasoning_effort = "medium"  # low, medium, high
max_context_length = 8192
```

### Tool Configuration
```ini
[TOOLS]
enable_python_tool = true
enable_browser_tool = false
enable_apply_patch_tool = false
```

## 📊 Data Structure

### Tasks
- **ID**: Unique identifier
- **Title & Description**: Task details
- **Priority**: Low, Medium, High, Urgent
- **Status**: Todo, In Progress, Completed, Cancelled
- **Due Date**: Optional deadline
- **Project Association**: Link to parent project
- **Tags**: Categorization labels
- **Time Tracking**: Estimated vs actual duration
- **Dependencies**: Tasks that must be completed first

### Projects
- **ID**: Unique identifier
- **Name & Description**: Project details
- **Status**: Todo, In Progress, Completed, Cancelled
- **Timeline**: Start and end dates
- **Progress**: Percentage completion
- **Milestones**: Key deliverables with target dates
- **Tags**: Categorization labels

### Calendar Events
- **ID**: Unique identifier
- **Title & Description**: Event details
- **Time**: Start and end times
- **Location**: Optional venue
- **Attendees**: Optional participant list
- **Recurrence**: Optional repeating pattern
- **Reminders**: Notification settings

## 🎯 Use Cases

### 1. Daily Life Management
- **Morning routine**: Check daily tasks and priorities
- **Task execution**: Work through prioritized list
- **Evening review**: Update progress and plan tomorrow

### 2. Project Management
- **Project setup**: Define scope, timeline, and milestones
- **Progress tracking**: Monitor completion and deadlines
- **Resource allocation**: Assign tasks and estimate time

### 3. Goal Achievement
- **Long-term planning**: Break down goals into projects
- **Milestone tracking**: Monitor progress toward objectives
- **Adjustment**: Modify plans based on progress

### 4. Productivity Optimization
- **Pattern analysis**: Identify productivity trends
- **Time management**: Optimize task scheduling
- **Priority management**: Focus on high-impact activities

## 🔄 Workflows

### Daily Planning Workflow
1. **Morning Review**: Check daily summary and suggestions
2. **Priority Setting**: Focus on urgent and high-priority tasks
3. **Time Blocking**: Schedule tasks throughout the day
4. **Progress Tracking**: Update task status as completed
5. **Evening Review**: Reflect on accomplishments and plan tomorrow

### Project Planning Workflow
1. **Project Definition**: Create project with scope and timeline
2. **Milestone Planning**: Define key deliverables and deadlines
3. **Task Breakdown**: Create specific tasks for each milestone
4. **Resource Allocation**: Assign time estimates and priorities
5. **Progress Monitoring**: Track completion and adjust timeline

### Weekly Review Workflow
1. **Productivity Analysis**: Review completion rates and patterns
2. **Priority Assessment**: Evaluate task priorities and deadlines
3. **Project Status**: Check milestone progress and blockers
4. **Planning**: Adjust upcoming week based on insights
5. **Goal Alignment**: Ensure activities support long-term objectives

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Change port in startup script
streamlit run personal_secretary_ui.py --server.port 8502
```

#### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt
```

#### Database Errors
```bash
# Reset database (WARNING: This will delete all data)
rm data/personal_secretary.db
```

#### GPT-OSS Model Issues
- Ensure you have the correct model files
- Check reasoning effort settings
- Verify context length limits

### Performance Optimization

#### Database Optimization
- Regular cleanup of completed tasks
- Archive old projects
- Optimize queries with proper indexing

#### Memory Management
- Limit context length for large datasets
- Use pagination for large task lists
- Clear chat history periodically

## 🔒 Security & Privacy

### Data Protection
- All data stored locally in SQLite database
- No external API calls without explicit configuration
- Optional browser tool requires API key setup

### Backup Recommendations
- Regular database backups
- Export task and project data
- Version control for configuration files

## 🎉 Advanced Features

### Custom Tools
Extend functionality by creating custom tools:
```python
class CustomTool:
    def __init__(self):
        self.tool_config = {
            "type": "function",
            "function": {
                "name": "custom_action",
                "description": "Your custom functionality",
                "parameters": {...}
            }
        }
```

### Integration Options
- **Calendar Integration**: Sync with Google Calendar, Outlook
- **Email Integration**: Process emails and create tasks
- **File Management**: Organize documents and resources
- **Time Tracking**: Automatic time logging

### Automation
- **Scheduled Reviews**: Automatic daily/weekly summaries
- **Deadline Alerts**: Proactive deadline notifications
- **Progress Reports**: Automated status updates
- **Smart Suggestions**: AI-powered recommendations

## 📚 Resources

### Documentation
- **Setup Guide**: `setup_personal_secretary.py`
- **Workflow Examples**: `workflow_examples.py`
- **Configuration**: `config.ini`

### Support
- Check the README.md for basic information
- Review workflow examples for usage patterns
- Use the chat interface for interactive help

## 🎯 Best Practices

### Task Management
1. **Be Specific**: Use clear, actionable task titles
2. **Set Priorities**: Use priority levels consistently
3. **Estimate Time**: Provide realistic time estimates
4. **Use Tags**: Categorize tasks for better organization
5. **Review Regularly**: Update status and progress

### Project Planning
1. **Define Scope**: Clear project boundaries and objectives
2. **Break Down**: Divide large projects into manageable tasks
3. **Set Milestones**: Define key deliverables and deadlines
4. **Track Progress**: Monitor completion and adjust timeline
5. **Document Lessons**: Learn from project experiences

### Productivity
1. **Daily Planning**: Start each day with a clear plan
2. **Priority Focus**: Concentrate on high-impact activities
3. **Time Blocking**: Allocate specific time for tasks
4. **Regular Reviews**: Assess progress and adjust approach
5. **Continuous Improvement**: Optimize based on insights

---

**Your GPT-OSS Personal Secretary is ready to transform how you manage your life!** 🚀

Start with the dashboard, explore the features, and let AI help you achieve your goals more effectively than ever before.