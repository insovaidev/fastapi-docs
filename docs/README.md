# FastAPI MySQL CRUD Documentation 🚀

Welcome to the documentation for the FastAPI MySQL CRUD project. This guide will walk you through the setup and execution process.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.9+**
- **Docker & Docker Compose** (Highly recommended for database setup)
- **MySQL Client** (Optional, for manual database management)

---

## ⚙️ Setup Instructions

### 1. Initialize the Environment
Clone the repository and navigate to the project root:
```powershell
git clone <repository-url>
cd fastapi-docs
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies:
```powershell
python -m venv .venv
# Activate on Windows (Command Prompt)
.\.venv\Scripts\activate
# Activate on Windows (PowerShell)
& .\.venv\Scripts\Activate.ps1
# Activate on Windows (Git Bash)
source .venv/Scripts/activate
# Activate on macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages:
```powershell
pip install -r requirements.txt
```

### 4. Configuration
Ensure your `.env` file is properly configured. A default `.env` is provided in the root:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fast_api
DB_USER=root
DB_PASSWORD=
```

---

## 🚀 Running the Project

### Step 1: Start the Database 🗄️
The easiest way to get the MySQL database running is via Docker Compose:
```powershell
docker-compose up -d
```
*Note: This will use the settings from your `.env` file.*

### Step 2: Start the Application ⚡
Run the FastAPI development server using Uvicorn:
```powershell
uvicorn app.main:app --reload
```
The server will start at **`http://127.0.0.1:8000`**.

---

## 📖 API Exploration

FastAPI provides built-in interactive documentation:

| Documentation Tool | URL |
| :--- | :--- |
| **Swagger UI** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| **ReDoc** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |

---

## 🏗️ Project Architecture

```text
app/
├── api/          # API route definitions (v1) : some api can call repository directly, others via service (if no complex business logic)
├── core/         # Global configuration & settings
├── db/           # Database connection & engine setup
├── models/       # SQLAlchemy database models
├── repositories/ # Data access layer patterns
├── schemas/      # Pydantic validation schemas
└── services/     # Business logic & orchestration
```

---

## 🛠️ Development Utilities

A `Makefile` is available for common tasks:
- **Pushing changes**: `make push` (Stages, commits, and pushes to master)
