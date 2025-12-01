# ITSM Incident Management System

A professional, lightweight Incident Management System built with Python and Flask. This application provides a robust platform for managing IT service requests and incidents with Role-Based Access Control (RBAC), real-time analytics, and a responsive user interface.

## 🚀 Features

### Core Functionalities
- **Incident Management**: Create, view, update, and track incidents through their lifecycle.
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Full access to all tickets, analytics dashboard, and assignment capabilities.
  - **Agent**: View and manage all tickets, update status, and accept assignments.
  - **User**: Create tickets and view only their own submitted requests.
- **Search & Filtering**: Advanced filtering by Category, Status, Priority, and text search by Title.
- **Pagination**: Efficient handling of large datasets with paginated views.
- **Responsive UI**: Built with Bootstrap 5 for a clean, mobile-friendly experience.

### Dashboard & Analytics (Admin View)
- **Key Metrics**: Real-time counters for Total Tickets.
- **Visual Breakdowns**:
  - Incidents by Priority (Critical, High, Medium, Low)
  - Incidents by Status (Open, In Progress, Resolved, Closed)
  - Incidents by Category (Hardware, Software, Network, Access, General)
- **Workload Analysis**: Track ticket distribution across agents.
- **SLA Monitoring**: "Open Ticket Age" buckets to identify stale tickets (< 1 Day, 1-3 Days, > 7 Days).

## 🛠️ Tech Stack

- **Backend**: Python 3.13, Flask 3.0
- **Database**: SQLite (via SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, Bootstrap 5, FontAwesome
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF

## ⚙️ Setup & Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory:
    ```bash
    cd python-flask-itsm-app
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database**:
    This script will create the database schema and populate it with **100 sample incidents** and default users for testing.
    ```bash
    python init_db.py
    ```

5.  **Run the Application**:
    ```bash
    python run.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## 🔐 Default Users & Credentials

The `init_db.py` script generates the following users for testing purposes. All passwords match the usernames.

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| **Admin** | `admin` | `admin` | Full system access, Dashboard analytics. |
| **Agent** | `agent1` | `agent1` | Can view/edit all tickets. |
| **Agent** | `agent2` - `agent5` | `agent2`... | Additional agents for workload testing. |
| **User** | `user1` | `user1` | Can only view/create their own tickets. |
| **User** | `user2` - `user5` | `user2`... | Additional standard users. |

## 📂 Project Structure

```
python-flask-itsm-app/
├── app/
│   ├── templates/      # HTML Templates (Jinja2)
│   ├── static/         # CSS, JS, Images
│   ├── __init__.py     # App Factory
│   ├── models.py       # Database Models (User, Incident)
│   ├── routes.py       # View Functions & Logic
│   ├── forms.py        # WTForms Definitions
│   └── auth.py         # Authentication Routes
├── init_db.py          # Database Seeding Script
├── run.py              # Application Entry Point
├── config.py           # Configuration Settings
└── requirements.txt    # Python Dependencies
```

## 📝 Usage Guide

1.  **Log in** using one of the credentials above.
2.  **Dashboard**:
    - **Admins** see the full analytics dashboard.
    - **Agents** see a list of all tickets.
    - **Users** see a list of their own tickets.
3.  **Create Incident**: Click "New Incident" to report an issue.
4.  **Search/Filter**: Use the top bar on the dashboard to find specific tickets.
5.  **Manage**: Click "View" on any ticket to update its status, priority, or assignment (Agents/Admins only).

## 🔌 REST API

The application exposes a RESTful API for external integrations.

### Endpoints

| Method | Endpoint | Description | Payload / Params |
|--------|----------|-------------|------------------|
| `GET` | `/api/incidents` | List all incidents | None |
| `GET` | `/api/incidents/<id>` | Get incident details | None |
| `POST` | `/api/incidents` | Create a new incident | JSON: `title`, `description`, `user_id` (required), `category`, `priority` (optional) |
| `PUT` | `/api/incidents/<id>` | Update an incident | JSON: `title`, `description`, `status`, `priority`, `category`, `assigned_to_id` |

### Testing with Python Client

A sample Python client is provided to test the API endpoints.

1.  Ensure the server is running (`python run.py`).
2.  Run the test client:
    ```bash
    python test_api_client.py
    ```

### Testing with cURL

You can also test the API using `curl` commands.

**1. Get All Incidents**
```bash
curl -X GET http://127.0.0.1:5000/api/incidents
```

**2. Create a New Incident**
```bash
curl -X POST http://127.0.0.1:5000/api/incidents \
     -H "Content-Type: application/json" \
     -d '{
           "title": "VPN Connection Issue",
           "description": "Unable to connect to VPN from remote office.",
           "user_id": 1,
           "category": "Network",
           "priority": "High"
         }'
```

**3. Update an Incident**
```bash
curl -X PUT http://127.0.0.1:5000/api/incidents/1 \
     -H "Content-Type: application/json" \
     -d '{
           "status": "In Progress",
           "priority": "Critical"
         }'
```
