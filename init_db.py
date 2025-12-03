from app import create_app, db
from app.models import User, Incident
import os
import random
from datetime import datetime, timedelta

app = create_app()

# Delete existing database to start fresh with new schema
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print("Existing database removed.")

with app.app_context():
    db.create_all()
    
    # Create Admin
    admin = User(username='admin', email='admin@example.com', role='Admin')
    admin.set_password('admin')
    db.session.add(admin)

    # Create 5 Agents
    agents = []
    for i in range(1, 6):
        agent = User(username=f'agent{i}', email=f'agent{i}@example.com', role='Agent')
        agent.set_password(f'agent{i}')
        agents.append(agent)
        db.session.add(agent)

    # Create 5 Users
    users = []
    for i in range(1, 6):
        user = User(username=f'user{i}', email=f'user{i}@example.com', role='User')
        user.set_password(f'user{i}')
        users.append(user)
        db.session.add(user)
    
    # Create AI Users
    ai_user = User(username='AI-User', email='ai-user@example.com', role='User')
    ai_user.set_password('AI-User')
    db.session.add(ai_user)
    # users.append(ai_user) # Excluded from random incident generation

    ai_agent = User(username='AI-SRE-Agent', email='ai-sre-agent@example.com', role='Agent')
    ai_agent.set_password('AI-SRE-Agent')
    db.session.add(ai_agent)
    # agents.append(ai_agent) # Excluded from random assignment

    db.session.commit()
    print("Users created: admin, 5 agents, 5 users, AI-User, AI-SRE-Agent")

    # Sample Data Lists
    categories = ['Hardware', 'Software', 'Network', 'Access', 'General']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    titles = [
        "System slow", "Cannot login", "Printer not working", "Wifi issue", 
        "Software update needed", "VPN down", "Email not syncing", "Blue screen error",
        "Keyboard malfunction", "Mouse broken", "Monitor flickering", "Access denied",
        "Password reset", "New account request", "Server unreachable"
    ]

    # Create 100 Sample Incidents
    incidents = []
    for i in range(100):
        # Randomize creation time (within last 30 days)
        days_ago = random.randint(0, 30)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        # Randomize status and assignee
        status = random.choice(statuses)
        assignee = None
        if status != 'Open':
            assignee = random.choice(agents)
        
        incident = Incident(
            title=f"{random.choice(titles)} - {i+1}",
            description=f"This is a sample description for incident #{i+1}. Please investigate.",
            category=random.choice(categories),
            priority=random.choice(priorities),
            status=status,
            created_at=created_at,
            author=random.choice(users),
            assignee=assignee
        )
        # If assigned, set assigned_to_id
        if assignee:
            incident.assigned_to_id = assignee.id
            
        incidents.append(incident)
    
    db.session.add_all(incidents)
    db.session.commit()
    print("100 Sample incidents created.")
    
    print("Database initialized successfully.")
