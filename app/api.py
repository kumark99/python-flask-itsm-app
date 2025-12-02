from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import Incident, User

bp = Blueprint('api', __name__)

@bp.route('/incidents', methods=['GET'])
def get_incidents():
    try:
        incidents = Incident.query.all()
        return jsonify([i.to_dict() for i in incidents])
    except Exception as e:
        current_app.logger.error(f"API Error getting incidents: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@bp.route('/incidents/<int:id>', methods=['GET'])
def get_incident(id):
    try:
        incident = Incident.query.get_or_404(id)
        return jsonify(incident.to_dict())
    except Exception as e:
        current_app.logger.error(f"API Error getting incident {id}: {str(e)}")
        return jsonify({'error': 'Not Found', 'message': 'Incident not found'}), 404

@bp.route('/incidents', methods=['POST'])
def create_incident():
    try:
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
        current_app.logger.info(f"API: New incident created by user {user.username}: {incident.title}")
        return jsonify(incident.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"API Error creating incident: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@bp.route('/incidents/<int:id>', methods=['PUT'])
def update_incident(id):
    try:
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
        current_app.logger.info(f"API: Incident {id} updated")
        return jsonify(incident.to_dict())
    except Exception as e:
        current_app.logger.error(f"API Error updating incident {id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
