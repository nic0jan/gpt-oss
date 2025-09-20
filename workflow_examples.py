#!/usr/bin/env python3
"""
Personal Secretary Example Workflows
Demonstrates various usage patterns and workflows
"""

import asyncio
import datetime
from typing import Dict, List, Any
from personal_secretary import PersonalSecretaryDatabase, PersonalSecretaryTools, Priority, Status
from gpt_oss_personal_secretary import GPTOSSPersonalSecretary

class PersonalSecretaryWorkflows:
    """Example workflows for the Personal Secretary"""
    
    def __init__(self):
        self.db = PersonalSecretaryDatabase("data/personal_secretary.db")
        self.tools = PersonalSecretaryTools(self.db)
        self.secretary = GPTOSSPersonalSecretary("data/personal_secretary.db")
    
    def workflow_daily_planning(self):
        """Daily planning workflow"""
        print("🌅 Daily Planning Workflow")
        print("=" * 40)
        
        # 1. Get daily summary
        summary = self.tools.get_daily_summary()
        print(f"📊 Today's Overview:")
        print(f"   - Tasks due today: {summary['today_tasks']}")
        print(f"   - Overdue tasks: {summary['overdue_tasks']}")
        print(f"   - High priority tasks: {summary['high_priority_tasks']}")
        
        # 2. Get suggestions
        suggestions = self.tools.suggest_next_actions()
        print(f"\n💡 Suggestions:")
        for suggestion in suggestions['suggestions']:
            print(f"   - {suggestion['message']}")
        
        # 3. Create morning routine tasks
        morning_tasks = [
            ("Check emails", "Review and respond to important emails", "high"),
            ("Daily standup", "Team meeting at 9 AM", "medium"),
            ("Review daily goals", "Check progress on weekly objectives", "medium")
        ]
        
        print(f"\n📝 Creating morning routine tasks...")
        for title, description, priority in morning_tasks:
            result = self.tools.create_task(
                title=title,
                description=description,
                priority=priority,
                due_date=datetime.datetime.now().replace(hour=10, minute=0, second=0).isoformat()
            )
            if result.get("success"):
                print(f"   ✅ Created: {title}")
        
        return "Daily planning completed"
    
    def workflow_project_setup(self):
        """Project setup workflow"""
        print("\n📁 Project Setup Workflow")
        print("=" * 40)
        
        # 1. Create a new project
        project_data = {
            "name": "Website Redesign Project",
            "description": "Complete redesign of company website with modern UI/UX",
            "start_date": datetime.datetime.now().isoformat(),
            "end_date": (datetime.datetime.now() + datetime.timedelta(days=90)).isoformat(),
            "tags": ["work", "web", "design"]
        }
        
        result = self.tools.create_project(**project_data)
        if result.get("success"):
            project_id = result["project_id"]
            print(f"✅ Created project: {project_data['name']}")
            
            # 2. Add milestones
            milestones = [
                ("Research & Planning", "Gather requirements and create wireframes", 7),
                ("Design Phase", "Create mockups and design system", 21),
                ("Development", "Implement frontend and backend", 45),
                ("Testing", "QA testing and bug fixes", 14),
                ("Launch", "Deploy to production", 3)
            ]
            
            print(f"\n🎯 Adding milestones...")
            for milestone_name, description, days_offset in milestones:
                target_date = datetime.datetime.now() + datetime.timedelta(days=days_offset)
                result = self.tools.add_milestone(
                    project_id=project_id,
                    milestone_name=milestone_name,
                    target_date=target_date.isoformat(),
                    description=description
                )
                if result.get("success"):
                    print(f"   ✅ Added milestone: {milestone_name}")
            
            # 3. Create project tasks
            project_tasks = [
                ("Conduct user research", "Interview users and analyze feedback", "high", 5),
                ("Create wireframes", "Design basic layout and navigation", "high", 3),
                ("Develop homepage", "Implement responsive homepage design", "medium", 7),
                ("Set up CI/CD", "Configure deployment pipeline", "medium", 2),
                ("Write documentation", "Create user and developer documentation", "low", 3)
            ]
            
            print(f"\n📋 Creating project tasks...")
            for title, description, priority, estimated_hours in project_tasks:
                result = self.tools.create_task(
                    title=title,
                    description=description,
                    priority=priority,
                    project_id=project_id,
                    estimated_duration=estimated_hours * 60  # Convert to minutes
                )
                if result.get("success"):
                    print(f"   ✅ Created task: {title}")
        
        return "Project setup completed"
    
    def workflow_productivity_analysis(self):
        """Productivity analysis workflow"""
        print("\n📈 Productivity Analysis Workflow")
        print("=" * 40)
        
        # 1. Analyze current productivity
        analysis = asyncio.run(self.secretary.personal_secretary_tool._analyze_productivity())
        productivity_data = analysis['productivity_analysis']
        
        print(f"📊 Productivity Metrics:")
        print(f"   - Completion rate: {productivity_data['completion_rate']}")
        print(f"   - Total tasks: {productivity_data['total_tasks']}")
        print(f"   - Completed tasks: {productivity_data['completed_tasks']}")
        print(f"   - Active projects: {productivity_data['active_projects']}")
        print(f"   - Average task duration: {productivity_data['average_task_duration_minutes']} minutes")
        
        # 2. Priority distribution analysis
        priority_dist = productivity_data['priority_distribution']
        print(f"\n🎯 Priority Distribution:")
        for priority, count in priority_dist.items():
            print(f"   - {priority.title()}: {count} tasks")
        
        # 3. Generate recommendations
        recommendations = []
        
        if productivity_data['completion_rate'] < "70%":
            recommendations.append("Consider breaking down large tasks into smaller, manageable pieces")
        
        if priority_dist.get('urgent', 0) > 3:
            recommendations.append("Too many urgent tasks - review priorities and delegate if possible")
        
        if productivity_data['average_task_duration_minutes'] > 120:
            recommendations.append("Tasks are taking longer than expected - consider time-blocking techniques")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        return "Productivity analysis completed"
    
    def workflow_weekly_planning(self):
        """Weekly planning workflow"""
        print("\n📅 Weekly Planning Workflow")
        print("=" * 40)
        
        # 1. Get weekly plan
        week_plan = asyncio.run(self.secretary.personal_secretary_tool._plan_week())
        
        print(f"📋 Weekly Overview:")
        overview = week_plan['weekly_overview']
        print(f"   - Total tasks: {overview['total_tasks']}")
        print(f"   - Urgent tasks: {overview['urgent_tasks']}")
        print(f"   - High priority tasks: {overview['high_priority_tasks']}")
        print(f"   - Estimated time: {overview['estimated_total_time_hours']} hours")
        print(f"   - Active projects: {overview['active_projects']}")
        
        # 2. Daily focus recommendations
        print(f"\n🎯 Daily Focus:")
        focus = week_plan['recommended_focus']
        for day, recommendation in focus.items():
            print(f"   - {day.title()}: {recommendation}")
        
        # 3. Priority tasks
        print(f"\n⭐ Priority Tasks:")
        for task in week_plan['priority_tasks'][:5]:
            print(f"   - {task['title']} ({task['priority']})")
        
        return "Weekly planning completed"
    
    def workflow_chat_interactions(self):
        """Chat interaction examples"""
        print("\n💬 Chat Interaction Examples")
        print("=" * 40)
        
        # Example chat interactions
        chat_examples = [
            "Create a task: Review quarterly reports, high priority, due tomorrow",
            "Show me today's summary",
            "What should I focus on next?",
            "Analyze my productivity",
            "Help me plan this week",
            "Create a project: Learn Spanish, start next Monday, 3 months duration",
            "Add a milestone to my website project: Complete user research by next Friday"
        ]
        
        print("📝 Example chat commands:")
        for i, example in enumerate(chat_examples, 1):
            print(f"   {i}. \"{example}\"")
        
        print(f"\n🤖 Sample responses:")
        
        # Simulate a few responses
        sample_responses = [
            "I'd be happy to help you create a task! To create a task effectively, I need a few details...",
            "📊 Daily Summary for 2024-01-15\nToday's Overview:\n- Tasks due today: 3\n- Overdue tasks: 1\n- High priority tasks: 2",
            "💡 Action Suggestions\nBased on your current tasks and priorities, I recommend focusing on the most urgent items first...",
            "📈 Productivity Analysis\nOverall Performance:\n- Task completion rate: 75%\n- Total tasks: 12\n- Completed tasks: 9"
        ]
        
        for i, response in enumerate(sample_responses, 1):
            print(f"   {i}. {response[:100]}...")
        
        return "Chat interaction examples completed"
    
    def workflow_automation_examples(self):
        """Automation workflow examples"""
        print("\n🤖 Automation Examples")
        print("=" * 40)
        
        # 1. Daily standup preparation
        print("📋 Daily Standup Preparation:")
        standup_tasks = self.db.get_tasks(status=Status.IN_PROGRESS)
        print(f"   - Active tasks: {len(standup_tasks)}")
        for task in standup_tasks[:3]:
            print(f"     • {task.title}")
        
        # 2. Weekly review automation
        print(f"\n📊 Weekly Review:")
        completed_this_week = [
            t for t in self.db.get_tasks(status=Status.COMPLETED)
            if t.updated_at.date() >= (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        ]
        print(f"   - Completed this week: {len(completed_this_week)}")
        
        # 3. Deadline reminders
        print(f"\n⏰ Upcoming Deadlines:")
        upcoming_tasks = [
            t for t in self.db.get_tasks()
            if t.due_date and 0 <= (t.due_date.date() - datetime.datetime.now().date()).days <= 3
        ]
        for task in upcoming_tasks[:3]:
            days_until = (task.due_date.date() - datetime.datetime.now().date()).days
            print(f"   - {task.title} (due in {days_until} days)")
        
        return "Automation examples completed"
    
    def run_all_workflows(self):
        """Run all example workflows"""
        print("🚀 Running All Personal Secretary Workflows")
        print("=" * 60)
        
        workflows = [
            self.workflow_daily_planning,
            self.workflow_project_setup,
            self.workflow_productivity_analysis,
            self.workflow_weekly_planning,
            self.workflow_chat_interactions,
            self.workflow_automation_examples
        ]
        
        results = []
        for workflow in workflows:
            try:
                result = workflow()
                results.append(result)
            except Exception as e:
                print(f"❌ Workflow failed: {e}")
                results.append(f"Failed: {e}")
        
        print(f"\n🎉 All workflows completed!")
        print(f"📋 Results:")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result}")

def main():
    """Main function to run example workflows"""
    workflows = PersonalSecretaryWorkflows()
    workflows.run_all_workflows()

if __name__ == "__main__":
    main()