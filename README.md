API Documentation
Swagger UI: http://localhost:8000/docs
Local Setup

1. Clone the repository

git clone <YOUR_REPO_URL> todo-integration-ml
cd todo-integration-ml


2. Create a virtual environment

python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate


3. Install dependencies

python -m pip install -U pip wheel
pip install -e .[dev]


4. Configure environment variables
Create a .env in the project root:

SECRET_KEY=dev-secret-change-me
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379/1
ACCESS_TOKEN_EXPIRE_MINUTES=60


5. Train the ML model (before using /predict)

python -m src.ml_infer --train data/tasks.csv


6. Run the app (locally or via Docker)

Local:

uvicorn src.app:app --reload


Docker:

docker compose up --build -d


7. Test the code

pytest
# or with coverage:
pytest --cov=src --cov-report=term-missing -q
