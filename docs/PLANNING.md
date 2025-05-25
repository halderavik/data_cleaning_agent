🧩 Project Overview
This project aims to build a scalable, intelligent survey data cleaning platform that processes SPSS files, detects low-quality responses using AI, and provides interactive tools for data review, rule configuration, and team collaboration.

⚙️ Tech Stack Overview
Component	Technology Choices
Frontend	React (w/ Next.js), Tailwind CSS, TypeScript, shadcn/ui, lucide-react
Backend APIs	Python (Flask or FastAPI), Node.js (optional for schema detection/validation)
ML Services	Python (Scikit-learn, PyTorch, Transformers, NumPyro), Sentence Transformers
Data Storage	PostgreSQL, AWS S3 (or MinIO for local dev), Redis (caching)
File Processing	Pyreadstat (SPSS), Pandas, NumPy
Infrastructure	Docker, Kubernetes (K8s), Terraform, GitHub Actions/GitLab CI for CI/CD
Authentication & RBAC	JWT, OAuth2.0, Role-based access using SQLAlchemy + Enums
Visualization/Reporting	Matplotlib, Seaborn, Plotly, ReportLab (PDFs)
Deployment	AWS (preferred): EC2, EKS, S3, Lambda, API Gateway, Amplify (for UI)
NLP/AI Services	Hugging Face Transformers, TextBlob, SpaCy, TfidfVectorizer, Zero-shot models
Logging & Monitoring	Sentry, Prometheus, Grafana, CloudWatch

🏗️ Project Directory Structure
bash
Copy
Edit
survey-data-cleaner/
├── frontend/             # Next.js/React UI
├── backend/              # Python Flask/FastAPI services
├── ml-services/          # AI/ML detection microservices
├── database/             # SQL scripts, migrations
├── infrastructure/       # Docker, K8s manifests, Terraform
└── docs/                 # PLANNING.md, architecture diagrams
🧠 ML/NLP Libraries
transformers (zero-shot, sentiment models, AI detection)

sentence-transformers (similarity)

scikit-learn, xgboost, lightgbm, pytorch

textblob, spacy, nltk (basic NLP)

NumPyro (for hierarchical models or HB modeling)

📦 Python Packages Required
bash
Copy
Edit
pip install pandas numpy pyreadstat scikit-learn textblob transformers \
            sentence-transformers flask fastapi uvicorn seaborn matplotlib \
            reportlab boto3 sqlalchemy alembic
🌐 API Layer
RESTful API using FastAPI or Flask

Swagger/OpenAPI for interactive docs

JWT-auth headers and role-based access middleware

Async job runners with Celery + Redis (optional for background tasks)

🖼️ Frontend Stack
React + Next.js for SSR & routing

Tailwind CSS + shadcn/ui for styling and component libraries

State management via Zustand or Context API

File uploads with drag-and-drop (e.g., react-dropzone)

Visualization components using D3/Chart.js/Recharts

🗂️ File Handling & Storage
Uploads: SPSS .sav files via frontend

File parsing: Python backend using pyreadstat

File storage:

Dev: Local FS / MinIO

Prod: AWS S3 (projects/{id}/raw/ etc.)

Backups before cleaning: Duplicate file storage (.backup.timestamp)

🧪 AI-Powered Cleaning Logic
Microservice Architecture for:

Duplicate detection (email, IP, response pattern)

Bot/speeder/straightliner detection

Open-end text analysis (profanity, brevity, plagiarism)

Geolocation & demographic anomaly checks

Conjoint satisficing patterns

Model deployment options:

REST endpoint using Flask

Hugging Face Transformers pipelines

Custom sklearn/PyTorch models served via FastAPI

📊 Reports & Dashboards
Quality scorecards with radar charts / line graphs

Executive summary PDFs: reportlab

Export formats: .sav, .csv, .xlsx, .json, .stata

🔒 Authentication & Permissions
JWT-based session management

UserRole enums: admin, manager, analyst, viewer

RBAC rules in SQLAlchemy + decorators

Per-project permission granularity

🔁 CI/CD & DevOps
GitHub Actions / GitLab CI: Test, lint, build pipelines

Dockerized services:

frontend/, backend/, ml-services/

Kubernetes for production deployment:

Autoscaling pods for ML inference

Environment configs: .env, config.yaml

🔌 Integration API
Public REST API (/projects, /upload, /clean, /export)

Webhooks: Triggered on project.created, file.uploaded, cleaning.completed, etc.

Rate limiting and access tokens via API Gateway

📈 Monitoring & Analytics
Logs: loguru or structlog (backend), Sentry (frontend)

Metrics: Prometheus, Grafana

AWS CloudWatch for serverless logs (if Lambda used)

🗃️ Database Schema (PostgreSQL)
projects, data_files, cleaning_checks, users, issues

Use alembic for migration versioning

Indexed by project_id, email, ip_address