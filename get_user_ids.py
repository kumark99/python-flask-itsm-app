from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    ai_user = User.query.filter_by(username='AI-User').first()
    ai_sre_agent = User.query.filter_by(username='AI-SRE-Agent').first()

    if ai_user:
        print(f"AI-User ID: {ai_user.id}")
    else:
        print("AI-User not found")

    if ai_sre_agent:
        print(f"AI-SRE-Agent ID: {ai_sre_agent.id}")
    else:
        print("AI-SRE-Agent not found")
