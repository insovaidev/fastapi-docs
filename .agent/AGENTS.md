# 🏗️ Project Structure (v2.0)

The project has been reorganized into a modular architecture to improve scalability, maintainability, and version control.

```text
.
├── app/                        # Main application package
│   ├── api/                    # API Route handlers
│   │   └── v1/
│   │       ├── api.py          # Main router for v1 (combines all endpoints)
│   │       └── endpoints/      # Individual route logic (users.py, validation.py, etc.)
│   ├── core/                   # Global configuration (config.py, settings)
│   ├── db/                     # Database connection and session management
│   ├── exceptions/             # Global exception handlers and error codes
│   ├── main.py                 # Application entry point & FastAPI instance
│   ├── models/                 # SQLAlchemy database models
│   ├── repositories/           # Data access layer (CRUD operations)
│   ├── schemas/                # Pydantic models (DTOs) for validation/serialization
│   ├── services/               # Complex business logic (optional orchestration layer)
│   └── tests/                  # Automated unit and integration tests
├── .agent/                     # Agent-specific logs, metadata, and instructions
│   ├── AGENTS.md               # Architecture and documentation (this file)
│   ├── LOG.txt                 # Runtime logs and error history
│   └── PROJECT                 # Project metadata
├── docs/                       # Project documentation
│   └── README.md               # Main setup and run guide
├── .env                        # Environment variables (DB credentials, ports)
├── db.sql                      # Database schema and seed data for initialization
├── docker-compose.yml          # Container configuration for MySQL
├── Makefile                    # Shortcut commands for development
└── requirements.txt            # Project dependencies
```

---

## 🛠️ Design Patterns

- **Repository Pattern**: Decouples the business logic from the data access layer, making it easier to swap databases or mock data for testing.
- **Dependency Injection**: Used via FastAPI's `Depends` for database sessions and configuration.
- **Asynchronous Support**: The project uses `aiomysql` and `AsyncSession` for non-blocking I/O operations.
- **Centralized Exception Handling**: All API exceptions are handled in `app/exceptions/handlers.py` to ensure consistent error responses.
