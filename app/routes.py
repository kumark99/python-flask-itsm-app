from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_required
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models import User, Incident
from app.forms import IncidentForm
import logging

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Search and Filter parameters
        search_query = request.args.get('q', '')
        filter_status = request.args.get('status', '')
        filter_priority = request.args.get('priority', '')
        filter_category = request.args.get('category', '')

        # Base Query
        if current_user.role == 'User':
            query = Incident.query.filter_by(user_id=current_user.id)
        else:
            query = Incident.query

        # Apply Search
        if search_query:
            query = query.filter(Incident.title.contains(search_query))
        
        # Apply Filters
        if filter_status:
            query = query.filter(Incident.status == filter_status)
        if filter_priority:
            query = query.filter(Incident.priority == filter_priority)
        if filter_category:
            query = query.filter(Incident.category == filter_category)

        # Pagination
        incidents_pagination = query.order_by(Incident.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        incidents = incidents_pagination.items
        
        stats = {}
        if current_user.role == 'Admin':
            # Calculate Stats
            stats['total'] = Incident.query.count()
            stats['by_priority'] = dict(db.session.query(Incident.priority, func.count(Incident.id)).group_by(Incident.priority).all())
            stats['by_category'] = dict(db.session.query(Incident.category, func.count(Incident.id)).group_by(Incident.category).all())
            stats['by_status'] = dict(db.session.query(Incident.status, func.count(Incident.id)).group_by(Incident.status).all())
            
            # By Agent
            stats['by_agent'] = dict(db.session.query(User.username, func.count(Incident.id)).join(Incident, Incident.assigned_to_id == User.id).group_by(User.username).all())
            
            # By User
            stats['by_user'] = dict(db.session.query(User.username, func.count(Incident.id)).join(Incident, Incident.user_id == User.id).group_by(User.username).all())
            
            # Age Buckets (Open tickets only)
            now = datetime.utcnow()
            open_incidents = Incident.query.filter(Incident.status.in_(['Open', 'In Progress'])).all()
            stats['age'] = {'< 1 Day': 0, '1-3 Days': 0, '3-7 Days': 0, '> 7 Days': 0}
            
            for inc in open_incidents:
                age = now - inc.created_at
                if age.days < 1:
                    stats['age']['< 1 Day'] += 1
                elif age.days < 3:
                    stats['age']['1-3 Days'] += 1
                elif age.days < 7:
                    stats['age']['3-7 Days'] += 1
                else:
                    stats['age']['> 7 Days'] += 1

        return render_template('dashboard.html', title='Dashboard', 
                            incidents=incidents, 
                            pagination=incidents_pagination, 
                            stats=stats,
                            search_query=search_query,
                            filter_status=filter_status,
                            filter_priority=filter_priority,
                            filter_category=filter_category)
    except Exception as e:
        current_app.logger.error(f"Error in index route: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'danger')
        return render_template('dashboard.html', title='Dashboard', incidents=[], pagination=None, stats={})

@bp.route('/incident/new', methods=['GET', 'POST'])
@login_required
def new_incident():
    try:
        form = IncidentForm()
        # Populate assignable users (Agents and Admins)
        agents = User.query.filter(User.role.in_(['Agent', 'Admin'])).all()
        form.assigned_to.choices = [(0, 'Unassigned')] + [(u.id, u.username) for u in agents]

        if form.validate_on_submit():
            incident = Incident(title=form.title.data, description=form.description.data,
                                category=form.category.data, priority=form.priority.data, author=current_user)
            if form.assigned_to.data != 0:
                incident.assigned_to_id = form.assigned_to.data
            
            db.session.add(incident)
            db.session.commit()
            current_app.logger.info(f"New incident created by {current_user.username}: {incident.title}")
            flash('Your incident has been reported!', 'success')
            return redirect(url_for('main.index'))
        return render_template('incident_form.html', title='New Incident', form=form, legend='New Incident')
    except Exception as e:
        current_app.logger.error(f"Error creating new incident: {str(e)}")
        db.session.rollback()
        flash('An error occurred while creating the incident.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/incident/<int:incident_id>', methods=['GET', 'POST'])
@login_required
def incident(incident_id):
    try:
        incident = Incident.query.get_or_404(incident_id)
        # Check permissions: User can only see their own, Agents/Admins can see all
        if current_user.role == 'User' and incident.author != current_user:
            current_app.logger.warning(f"Unauthorized access attempt by {current_user.username} to incident {incident_id}")
            abort(403)

        form = IncidentForm()
        agents = User.query.filter(User.role.in_(['Agent', 'Admin'])).all()
        form.assigned_to.choices = [(0, 'Unassigned')] + [(u.id, u.username) for u in agents]

        if form.validate_on_submit():
            incident.title = form.title.data
            incident.description = form.description.data
            incident.category = form.category.data
            incident.priority = form.priority.data
            incident.status = form.status.data
            
            if current_user.role in ['Agent', 'Admin']:
                if form.assigned_to.data != 0:
                    incident.assigned_to_id = form.assigned_to.data
                else:
                    incident.assigned_to_id = None
                
            db.session.commit()
            current_app.logger.info(f"Incident {incident_id} updated by {current_user.username}")
            flash('Incident has been updated!', 'success')
        elif request.method == 'GET':
            form.title.data = incident.title
            form.description.data = incident.description
            form.category.data = incident.category
            form.priority.data = incident.priority
            form.status.data = incident.status
            form.assigned_to.data = incident.assigned_to_id if incident.assigned_to_id else 0

        return render_template('incident_form.html', title='Incident Details', form=form, legend='Incident Details', incident=incident)
    except Exception as e:
        current_app.logger.error(f"Error accessing/updating incident {incident_id}: {str(e)}")
        db.session.rollback()
        flash('An error occurred while processing the incident.', 'danger')
        return redirect(url_for('main.index'))
