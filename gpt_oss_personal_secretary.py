#!/usr/bin/env python3
"""
GPT-OSS Personal Secretary Integration
Integrates the personal secretary with GPT-OSS for intelligent assistance
"""

import asyncio
import json
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Import GPT-OSS components
from gpt_oss.tools.python_docker.docker_tool import PythonTool
from gpt_oss.tools.simple_browser import SimpleBrowserTool
from gpt_oss.tools.simple_browser.backend import ExaBackend
from openai_harmony import SystemContent, Message, Conversation, Role, load_harmony_encoding, HarmonyEncodingName

from personal_secretary import PersonalSecretaryDatabase, PersonalSecretaryTools, Task, Project, Priority, Status

logger = logging.getLogger(__name__)

class PersonalSecretaryTool:
    """Custom tool for GPT-OSS to interact with personal secretary functionality"""
    
    def __init__(self, db_path: str = "personal_secretary.db"):
        self.db = PersonalSecretaryDatabase(db_path)
        self.tools = PersonalSecretaryTools(self.db)
        self.tool_config = {
            "type": "function",
            "function": {
                "name": "personal_secretary",
                "description": "Manage personal agenda, tasks, projects, and life planning",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "create_task", "update_task", "list_tasks", "create_project",
                                "add_milestone", "list_projects", "daily_summary", "suggest_actions",
                                "schedule_event", "analyze_productivity", "plan_week"
                            ],
                            "description": "The action to perform"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parameters for the action"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    async def process(self, message) -> List[Message]:
        """Process a message from GPT-OSS"""
        try:
            # Parse the message content
            content = message.content
            if hasattr(content, 'function_call'):
                function_call = content.function_call
                action = function_call.name
                params = json.loads(function_call.arguments) if function_call.arguments else {}
            else:
                # Handle text-based commands
                return await self._handle_text_command(content)
            
            # Execute the action
            result = await self._execute_action(action, params)
            
            # Create response message
            response_content = f"Personal Secretary: {json.dumps(result, indent=2)}"
            response_message = Message.from_role_and_content(Role.ASSISTANT, response_content)
            
            return [response_message]
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_message = Message.from_role_and_content(
                Role.ASSISTANT, 
                f"Error: {str(e)}"
            )
            return [error_message]
    
    async def _handle_text_command(self, content: str) -> List[Message]:
        """Handle natural language commands"""
        content_lower = content.lower()
        
        if "create task" in content_lower or "add task" in content_lower:
            # Extract task information from natural language
            # This is a simplified version - in practice, you'd use NLP to extract details
            result = {"message": "Please use the structured function call to create tasks with specific parameters"}
        elif "daily summary" in content_lower or "today's tasks" in content_lower:
            result = self.tools.get_daily_summary()
        elif "suggestions" in content_lower or "what should i do" in content_lower:
            result = self.tools.suggest_next_actions()
        else:
            result = {"message": "I can help you manage tasks, projects, and your schedule. Try asking me to create a task, show your daily summary, or get suggestions for what to do next."}
        
        response_message = Message.from_role_and_content(Role.ASSISTANT, json.dumps(result, indent=2))
        return [response_message]
    
    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified action with given parameters"""
        try:
            if action == "create_task":
                return self.tools.create_task(
                    title=params.get("title", ""),
                    description=params.get("description", ""),
                    priority=params.get("priority", "medium"),
                    due_date=params.get("due_date"),
                    project_id=params.get("project_id"),
                    tags=params.get("tags", []),
                    estimated_duration=params.get("estimated_duration")
                )
            
            elif action == "update_task":
                return self.tools.update_task_status(
                    task_id=params.get("task_id"),
                    status=params.get("status")
                )
            
            elif action == "list_tasks":
                status = params.get("status")
                project_id = params.get("project_id")
                tasks = self.db.get_tasks(
                    status=Status(status) if status else None,
                    project_id=project_id
                )
                return {
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "priority": t.priority.value,
                            "status": t.status.value,
                            "due_date": t.due_date.isoformat() if t.due_date else None,
                            "project_id": t.project_id,
                            "tags": t.tags
                        }
                        for t in tasks
                    ]
                }
            
            elif action == "create_project":
                return self.tools.create_project(
                    name=params.get("name", ""),
                    description=params.get("description", ""),
                    start_date=params.get("start_date"),
                    end_date=params.get("end_date"),
                    tags=params.get("tags", [])
                )
            
            elif action == "add_milestone":
                return self.tools.add_milestone(
                    project_id=params.get("project_id"),
                    milestone_name=params.get("milestone_name"),
                    target_date=params.get("target_date"),
                    description=params.get("description", "")
                )
            
            elif action == "list_projects":
                status = params.get("status")
                projects = self.db.get_projects(status=Status(status) if status else None)
                return {
                    "projects": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "description": p.description,
                            "status": p.status.value,
                            "start_date": p.start_date.isoformat() if p.start_date else None,
                            "end_date": p.end_date.isoformat() if p.end_date else None,
                            "progress_percentage": p.progress_percentage,
                            "milestones": p.milestones,
                            "tags": p.tags
                        }
                        for p in projects
                    ]
                }
            
            elif action == "daily_summary":
                return self.tools.get_daily_summary()
            
            elif action == "suggest_actions":
                return self.tools.suggest_next_actions()
            
            elif action == "analyze_productivity":
                return await self._analyze_productivity()
            
            elif action == "plan_week":
                return await self._plan_week()
            
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {"error": str(e)}
    
    async def _analyze_productivity(self) -> Dict[str, Any]:
        """Analyze productivity patterns and provide insights"""
        tasks = self.db.get_tasks()
        projects = self.db.get_projects()
        
        # Calculate completion rates
        completed_tasks = [t for t in tasks if t.status == Status.COMPLETED]
        total_tasks = len(tasks)
        completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0
        
        # Analyze priority distribution
        priority_dist = {}
        for task in tasks:
            if task.status != Status.COMPLETED:
                priority_dist[task.priority.value] = priority_dist.get(task.priority.value, 0) + 1
        
        # Calculate average task duration
        tasks_with_duration = [t for t in completed_tasks if t.actual_duration]
        avg_duration = sum(t.actual_duration for t in tasks_with_duration) / len(tasks_with_duration) if tasks_with_duration else 0
        
        return {
            "productivity_analysis": {
                "completion_rate": f"{completion_rate:.1%}",
                "total_tasks": total_tasks,
                "completed_tasks": len(completed_tasks),
                "priority_distribution": priority_dist,
                "average_task_duration_minutes": round(avg_duration, 1),
                "active_projects": len([p for p in projects if p.status == Status.IN_PROGRESS])
            }
        }
    
    async def _plan_week(self) -> Dict[str, Any]:
        """Generate a weekly plan based on current tasks and projects"""
        tasks = self.db.get_tasks(status=Status.TODO)
        projects = self.db.get_projects(status=Status.IN_PROGRESS)
        
        # Group tasks by priority
        urgent_tasks = [t for t in tasks if t.priority == Priority.URGENT]
        high_priority_tasks = [t for t in tasks if t.priority == Priority.HIGH]
        medium_priority_tasks = [t for t in tasks if t.priority == Priority.MEDIUM]
        
        # Calculate estimated time needed
        total_estimated_time = sum(t.estimated_duration or 60 for t in tasks)  # Default 60 min if not specified
        
        week_plan = {
            "weekly_overview": {
                "total_tasks": len(tasks),
                "urgent_tasks": len(urgent_tasks),
                "high_priority_tasks": len(high_priority_tasks),
                "estimated_total_time_hours": round(total_estimated_time / 60, 1),
                "active_projects": len(projects)
            },
            "recommended_focus": {
                "monday": "Focus on urgent tasks and high-priority items",
                "tuesday": "Continue high-priority tasks and start medium-priority items",
                "wednesday": "Work on project milestones and medium-priority tasks",
                "thursday": "Complete remaining medium-priority tasks and review progress",
                "friday": "Wrap up week's tasks and plan for next week"
            },
            "priority_tasks": [
                {"id": t.id, "title": t.title, "priority": t.priority.value}
                for t in urgent_tasks[:5] + high_priority_tasks[:5]
            ]
        }
        
        return week_plan

class GPTOSSPersonalSecretary:
    """Main class for GPT-OSS Personal Secretary"""
    
    def __init__(self, db_path: str = "personal_secretary.db"):
        self.db_path = db_path
        self.personal_secretary_tool = PersonalSecretaryTool(db_path)
        self.python_tool = PythonTool()
        self.browser_tool = None  # Initialize if needed
        
        # Load harmony encoding
        self.encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
        
        # Create system prompt
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the personal secretary"""
        return """You are an intelligent personal secretary powered by GPT-OSS. Your role is to help manage:

1. **Task Management**: Create, update, and track personal and professional tasks
2. **Project Planning**: Help plan and monitor projects with milestones and deadlines
3. **Schedule Management**: Organize calendar events and appointments
4. **Productivity Analysis**: Analyze work patterns and suggest improvements
5. **Life Planning**: Provide strategic advice for personal and professional goals

**Key Capabilities:**
- Create tasks with priorities, due dates, and project associations
- Track project progress and manage milestones
- Analyze productivity patterns and suggest optimizations
- Generate daily summaries and weekly plans
- Provide intelligent suggestions for next actions

**Communication Style:**
- Be proactive and helpful
- Provide clear, actionable advice
- Ask clarifying questions when needed
- Offer multiple options when appropriate
- Be encouraging and supportive

**Available Tools:**
- personal_secretary: Manage tasks, projects, and schedule
- python: Execute calculations and data analysis
- browser: Search for information when needed

Always prioritize user's goals and provide practical, implementable suggestions."""

    async def chat(self, user_message: str, use_python: bool = True, use_browser: bool = False) -> str:
        """Main chat interface"""
        try:
            # Create system message with tools
            system_content = SystemContent.new().with_conversation_start_date(
                datetime.datetime.now().strftime("%Y-%m-%d")
            )
            
            # Add tools
            tools = [self.personal_secretary_tool.tool_config]
            if use_python:
                tools.append(self.python_tool.tool_config)
            if use_browser and self.browser_tool:
                tools.append(self.browser_tool.tool_config)
            
            system_content = system_content.with_tools(tools)
            
            # Create messages
            system_message = Message.from_role_and_content(Role.SYSTEM, system_content)
            user_msg = Message.from_role_and_content(Role.USER, user_message)
            
            conversation = Conversation.from_messages([system_message, user_msg])
            
            # Convert to tokens (this would normally go to GPT-OSS model)
            # For now, we'll simulate the response
            response = await self._simulate_gpt_oss_response(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error: {str(e)}"
    
    async def _simulate_gpt_oss_response(self, user_message: str) -> str:
        """Simulate GPT-OSS response for demonstration"""
        # In a real implementation, this would call the actual GPT-OSS model
        # For now, we'll provide intelligent responses based on the message content
        
        message_lower = user_message.lower()
        
        if "create task" in message_lower or "add task" in message_lower:
            return """I'd be happy to help you create a task! To create a task effectively, I need a few details:

1. **Task title**: What's the main task?
2. **Description**: Any additional details?
3. **Priority**: Low, medium, high, or urgent?
4. **Due date**: When should this be completed?
5. **Project**: Is this part of a larger project?
6. **Estimated time**: How long do you think it will take?

For example: "Create a task: Review quarterly reports, high priority, due tomorrow, part of Q4 review project, estimated 2 hours"

Would you like to provide these details so I can create the task for you?"""

        elif "daily summary" in message_lower or "today" in message_lower:
            summary = self.personal_secretary_tool.tools.get_daily_summary()
            return f"""📊 **Daily Summary for {summary['date']}**

**Today's Overview:**
- Tasks due today: {summary['today_tasks']}
- Overdue tasks: {summary['overdue_tasks']}
- High priority tasks: {summary['high_priority_tasks']}

**Key Tasks:**
{self._format_task_list(summary['tasks'][:5])}

Would you like me to help you prioritize these tasks or create a plan for the day?"""

        elif "suggest" in message_lower or "what should i do" in message_lower:
            suggestions = self.personal_secretary_tool.tools.suggest_next_actions()
            return f"""💡 **Action Suggestions**

{self._format_suggestions(suggestions['suggestions'])}

Based on your current tasks and priorities, I recommend focusing on the most urgent items first. Would you like me to help you create a detailed action plan?"""

        elif "analyze" in message_lower or "productivity" in message_lower:
            analysis = await self.personal_secretary_tool._analyze_productivity()
            return f"""📈 **Productivity Analysis**

**Overall Performance:**
- Task completion rate: {analysis['productivity_analysis']['completion_rate']}
- Total tasks: {analysis['productivity_analysis']['total_tasks']}
- Completed tasks: {analysis['productivity_analysis']['completed_tasks']}
- Active projects: {analysis['productivity_analysis']['active_projects']}

**Priority Distribution:**
{self._format_priority_distribution(analysis['productivity_analysis']['priority_distribution'])}

**Average task duration:** {analysis['productivity_analysis']['average_task_duration_minutes']} minutes

Would you like me to suggest ways to improve your productivity based on this analysis?"""

        else:
            return """Hello! I'm your intelligent personal secretary powered by GPT-OSS. I'm here to help you manage your life more effectively.

**What I can help you with:**
- 📝 **Task Management**: Create, update, and track tasks
- 📋 **Project Planning**: Plan projects with milestones and deadlines  
- 📅 **Schedule Management**: Organize your calendar and appointments
- 📊 **Productivity Analysis**: Analyze your work patterns
- 🎯 **Life Planning**: Strategic advice for your goals

**Try asking me:**
- "Create a task: Review quarterly reports, high priority, due tomorrow"
- "Show me today's summary"
- "What should I focus on next?"
- "Analyze my productivity"
- "Help me plan this week"

What would you like to work on today?"""

    def _format_task_list(self, tasks: List[Dict]) -> str:
        """Format task list for display"""
        if not tasks:
            return "No tasks found."
        
        formatted = []
        for task in tasks:
            priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
            formatted.append(f"{priority_emoji} {task['title']} ({task['status']})")
        
        return "\n".join(formatted)
    
    def _format_suggestions(self, suggestions: List[Dict]) -> str:
        """Format suggestions for display"""
        if not suggestions:
            return "No specific suggestions at this time."
        
        formatted = []
        for suggestion in suggestions:
            formatted.append(f"**{suggestion['type'].replace('_', ' ').title()}:** {suggestion['message']}")
        
        return "\n\n".join(formatted)
    
    def _format_priority_distribution(self, dist: Dict[str, int]) -> str:
        """Format priority distribution for display"""
        if not dist:
            return "No active tasks."
        
        formatted = []
        for priority, count in dist.items():
            emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
            formatted.append(f"{emoji} {priority.title()}: {count} tasks")
        
        return "\n".join(formatted)

async def main():
    """Demo the GPT-OSS Personal Secretary"""
    print("🤖 GPT-OSS Personal Secretary")
    print("=" * 50)
    
    secretary = GPTOSSPersonalSecretary()
    
    # Demo interactions
    demo_messages = [
        "Hello! I need help managing my tasks and projects.",
        "Show me today's summary",
        "What should I focus on next?",
        "Create a task: Review quarterly reports, high priority, due tomorrow",
        "Analyze my productivity"
    ]
    
    for message in demo_messages:
        print(f"\n👤 User: {message}")
        response = await secretary.chat(message)
        print(f"🤖 Secretary: {response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())