# Smart Support Desk System

Smart Support Desk is a comprehensive ticketing and customer management system designed for support agents and administrators. It features a FastAPI backend with Redis caching and a Streamlit-based frontend for an interactive user experience.

## Features

* **Dashboard**: Visualize ticket statistics, including breakdown by priority, status, and type, as well as employee performance metrics.
* **Ticket Management**: Create, update, assign, and track support tickets through various stages such as Open, In Progress, and Closed.
* **Customer Management**: Maintain a database of customers, their companies, and contact information.
* **Employee Roles**: Support for `admin` and `agent` access levels with different permissions.
* **Note System**: Add internal notes to tickets for better collaboration among agents.
* **Caching**: Redis integration for optimized performance on dashboard and listing endpoints.

## Tech Stack

* **Backend**: FastAPI
* **Frontend**: Streamlit
* **Database**: SQLAlchemy ORM 
* **Caching**: Redis

---

## Installation and Setup

### Prerequisites

* Python 3.10 or higher
* Redis server (Running on `localhost:32768` by default)
* A SQL Database (configured via environment variables)

### 1. Clone the Repository
```bash
git clone https://github.com/Kavish05-Turabit/Smart_Support_Desk
cd Smart_Support_Desk
```

### 2. Backend Setup
#### Install libraries
```bash
pip install -r requirements.txt
```
#### Navigate to server
```bash
cd backend
```
#### Create a `.env` file in the root of the backend directory with the following variables:
```
DATABASE_URL=your_sql_database_url
JWT_SHA256_HASH=your_secret_hash
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
#### Start backend server
```bash
uvicorn app.main:app --port 8000 --reload
```
(The API docs will be available at http://localhost:8000/docs)
### 3. Frontend Setup
#### Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```
#### Run the Streamlit application:
```bash
streamlit run main.py
```
(The frontend will be available at http://localhost:8501)

## Project Structure

* `backend/app/api/`: API route definitions for customers, tickets, employees, and dashboard.
* `backend/app/core/`: Core logic including authentication, security, and database session management.
* `backend/app/models/`: SQLAlchemy models and Pydantic validation schemas.
* `frontend/views/`: Individual Streamlit pages for the application.
* `frontend/utils/`: Helper functions for charts and dialogs.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.
