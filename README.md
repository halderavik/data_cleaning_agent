# Survey Data Cleaning Platform

An AI-powered platform for cleaning and validating survey data files with enterprise-grade security and extensive third-party integrations.

## Features

### Core Features
- Support for multiple file formats (SPSS, CSV, Excel, JSON)
- 27+ predefined validation rules
- AI-powered intelligence features
- Interactive review interface
- Comprehensive reporting
- Team collaboration capabilities

### Advanced Features
- **Data Security**
  - End-to-end encryption for data at rest and in transit
  - Role-based access control (RBAC)
  - Comprehensive audit logging
  - Automatic key rotation
  - Data masking and anonymization
  - GDPR and HIPAA compliance support

- **Integration Capabilities**
  - **Survey Platforms**
    - Qualtrics
    - SurveyMonkey
    - Google Forms
    - Microsoft Forms
    - Typeform
  
  - **Data Storage**
    - AWS S3
    - Google Cloud Storage
    - Azure Blob Storage
    - Dropbox
    - Box
  
  - **Analytics & BI**
    - Tableau
    - Power BI
    - Looker
    - Google Data Studio
    - Metabase
  
  - **CRM & Marketing**
    - Salesforce
    - HubSpot
    - Mailchimp
    - Marketo
    - Pardot

- **AI/ML Features**
  - Automated data quality assessment
  - Anomaly detection
  - Pattern recognition
  - Sentiment analysis
  - Text classification
  - Data imputation
  - Outlier detection

## Tech Stack

### Frontend
- React with Next.js
- Tailwind CSS
- TypeScript
- shadcn/ui
- lucide-react

### Backend
- Python with FastAPI
- PostgreSQL
- Redis
- AWS S3

### ML/AI
- Scikit-learn
- PyTorch
- Transformers
- Sentence Transformers
- TextBlob
- SpaCy
- NumPyro

### Security
- JWT Authentication
- OAuth2 Integration
- Fernet Encryption
- Role-Based Access Control
- Audit Logging

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis
- Node.js 16+
- AWS Account (for file storage)

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following variables:
```
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/survey_cleaning

# Security Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your-encryption-key
ENCRYPTION_SALT=your-encryption-salt

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket-name

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Integration API Keys
QUALTRICS_API_KEY=your-qualtrics-key
SURVEYMONKEY_API_KEY=your-surveymonkey-key
SALESFORCE_API_KEY=your-salesforce-key
```

4. Initialize the database:
```bash
# Create database
createdb survey_cleaning

# Run migrations
alembic upgrade head
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Usage Guide

### Data Security

1. **Access Control**
   - Configure user roles and permissions
   - Set up data access policies
   - Enable multi-factor authentication
   - Configure session timeouts

2. **Data Encryption**
   - Enable end-to-end encryption
   - Configure key rotation policies
   - Set up data masking rules
   - Configure audit logging

3. **Compliance**
   - Enable GDPR compliance features
   - Configure data retention policies
   - Set up data export capabilities
   - Enable consent management

### Third-Party Integrations

1. **Survey Platform Integration**
   ```python
   # Example: Qualtrics Integration
   from services.integration_service import IntegrationService
   
   integration = IntegrationService()
   survey_data = integration.get_qualtrics_survey(survey_id="SV_123456")
   ```

2. **Data Storage Integration**
   ```python
   # Example: AWS S3 Integration
   from services.storage_service import StorageService
   
   storage = StorageService()
   storage.upload_file(file_path="data.sav", bucket="survey-data")
   ```

3. **Analytics Integration**
   ```python
   # Example: Tableau Integration
   from services.analytics_service import AnalyticsService
   
   analytics = AnalyticsService()
   analytics.export_to_tableau(data_source="cleaned_survey")
   ```

### API Usage

1. **Authentication**
   ```bash
   # Get access token
   curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "pass"}'
   ```

2. **Data Processing**
   ```bash
   # Upload and process file
   curl -X POST http://localhost:8000/api/v1/process \
     -H "Authorization: Bearer <token>" \
     -F "file=@survey.sav"
   ```

3. **Integration Management**
   ```bash
   # Configure integration
   curl -X POST http://localhost:8000/api/v1/integrations \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"type": "qualtrics", "config": {"api_key": "key"}}'
   ```

## Development

### Project Structure

```
.
├── backend/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── security/
│   │   ├── integration/
│   │   └── analytics/
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── public/
│   ├── styles/
│   └── tests/
├── ml-services/
│   ├── models/
│   ├── training/
│   └── inference/
└── infrastructure/
    ├── docker/
    └── kubernetes/
```

### Testing

Run backend tests:
```bash
pytest
```

Run frontend tests:
```bash
cd frontend
npm test
```

### Security Testing
```bash
# Run security tests
pytest tests/security/

# Run integration tests
pytest tests/integration/

# Run performance tests
pytest tests/performance/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the [documentation]
2. Open an issue in the repository
3. Contact support@surveycleaning.com 