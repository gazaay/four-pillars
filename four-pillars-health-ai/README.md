# Four Pillars Health AI

A comprehensive system using AI models to provide health expert advice, policy information, and patient history management through a chat interface.

## Features

- **Multi-model AI Chat Interface**: Utilizes multiple AI models specialized in different healthcare domains.
- **Health Database Integration**: Connect to and query medical databases for patient history.
- **Expert Health Advice**: Provides evidence-based health recommendations.
- **Policy Information**: Keeps users informed about relevant healthcare policies.
- **Secure Patient Data Handling**: Ensures compliance with healthcare data protection regulations.

## Project Structure

```
four-pillars-health-ai/
├── app/
│   ├── api/         # FastAPI routes and endpoints
│   ├── models/      # AI model integrations and data models
│   ├── database/    # Database schemas and connection utilities
│   ├── services/    # Business logic layer 
│   ├── utils/       # Helper functions and utilities
│   └── config/      # Configuration files
├── tests/           # Test suite
├── alembic/         # Database migration files
├── .env             # Environment variables (not tracked in git)
├── requirements.txt # Project dependencies
└── README.md        # Project documentation
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with required environment variables
6. Run database migrations: `alembic upgrade head`
7. Start the server: `uvicorn app.main:app --reload`

## Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- Other model API keys as needed

## API Documentation

When running locally, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 