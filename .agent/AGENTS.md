.
├── app/                  # Main application package
│   ├── __init__.py       # Makes 'app' a Python package
│   ├── main.py           # Application entry point & FastAPI instance
│   ├── api/              # API Route handlers (v1, v2, etc.)
│   │   ├── v1/
│   │   │   ├── api.py    # Main router including sub-routers
│   │   │   └── endpoints/# Individual endpoint modules (e.g., users.py)
│   ├── core/             # Global config (settings, security, constants)
│   ├── repositories/             # Create, Read, Update, Delete logic
│   ├── db/               # Database connection and session management
│   ├── models/           # SQLAlchemy or SQLModel database models
│   ├── schemas/          # Pydantic models for data validation/serialization
│   ├── services/         # Complex business logic (optional layer)
│   └── tests/            # Unit and integration tests
├── .env                  # Environment variables
├── requirements.txt      # Project dependencies
└── docker-compose.yml    # Container configuration
