from flask import Blueprint, jsonify, request
from app import db
from app.models import Incident, User

bp = Blueprint('api', __name__)

@bp.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = Incident.query.all()
    return jsonify([i.to_dict() for i in incidents])

@bp.route('/incidents/<int:id>', methods=['GET'])
def get_incident(id):
    incident = Incident.query.get_or_404(id)
    return jsonify(incident.to_dict())

@bp.route('/incidents', methods=['POST'])
def create_incident():
    data = request.get_json() or {}
    if 'title' not in data or 'description' not in data or 'user_id' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Must include title, description and user_id'}), 400
    
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'Bad Request', 'message': 'User not found'}), 400

    incident = Incident(
        title=data['title'],
        description=data['description'],
        category=data.get('category', 'General'),
        priority=data.get('priority', 'Medium'),
        author=user
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify(incident.to_dict()), 201

@bp.route('/incidents/<int:id>', methods=['PUT'])
def update_incident(id):
    incident = Incident.query.get_or_404(id)
    data = request.get_json() or {}
    
    if 'title' in data:
        incident.title = data['title']
    if 'description' in data:
        incident.description = data['description']
    if 'category' in data:
        incident.category = data['category']
    if 'status' in data:
        incident.status = data['status']
    if 'priority' in data:
        incident.priority = data['priority']
    if 'assigned_to_id' in data:
        incident.assigned_to_id = data['assigned_to_id']

    db.session.commit()
    return jsonify(incident.to_dict())
