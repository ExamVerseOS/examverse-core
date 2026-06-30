# examverse-core 🔧

**Repository:** https://github.com/ExamVerseOS/examverse-core  
**Purpose:** Shared business logic, common models, utilities, and configuration  
**Owner:** Backend Team / Tech Lead  
**Status:** 🔄 Phase 1 - MVP Foundation

---

## 📖 What is This Repository?

`examverse-core` is the **shared code library** for the entire ExamVerseOS backend. It contains reusable code that multiple services (examverse-api, examverse-ingestion, etc.) import and use.

This is where you put:
- ✅ Database models and schemas
- ✅ Configuration management
- ✅ Logging setup
- ✅ Common exceptions & error handling
- ✅ Utility functions
- ✅ Constants and enums
- ✅ Shared validation logic
- ✅ Authentication utilities (Phase 2)

This is NOT where you put:
- ❌ Service-specific logic
- ❌ API endpoints
- ❌ Business workflows
- ❌ Ingestion pipelines

---

## 🎯 Role in the ExamVerseOS Network

```
                    examverse-core
                   Shared Library
                        │
        ┌───────────────┼───────────────┐
        │               │               │
     Imports        Imports        Imports
        │               │               │
        ▼               ▼               ▼
   examverse-api  examverse-ingestion  examverse-ai
   Backend API    Data Pipeline        AI Services
```

**Key Relationships:**
- 📦 **Imported by:** examverse-api, examverse-ingestion, examverse-ai
- 📤 **Exports to:** Database models, config, logging, utilities
- 📥 **Imports from:** examverse-db (for migrations)
- 🔄 **Updated by:** All backend teams (when adding shared code)
- ⚡ **Dependency:** examverse-db (for database migration tools)

---

## 📁 Repository Structure

```
examverse-core/
│
├─ README.md (this file)
├─ pyproject.toml (Python package config)
├─ setup.py (Python package setup)
├─ requirements.txt (Dependencies)
├─ requirements-dev.txt (Dev dependencies)
│
├─ examverse_core/
│  │
│  ├─ __init__.py
│  ├─ __version__.py (Version: 0.1.0, then 0.2.0, etc.)
│  │
│  ├─ database/
│  │  ├─ __init__.py
│  │  ├─ models.py
│  │  │  ├─ class Base (SQLAlchemy base)
│  │  │  ├─ class User(Base)
│  │  │  ├─ class Exam(Base)
│  │  │  ├─ class Topic(Base)
│  │  │  ├─ class Question(Base)
│  │  │  ├─ class StudyPlan(Base)
│  │  │  └─ ... all database models
│  │  │
│  │  ├─ schemas.py (Pydantic schemas for validation)
│  │  │  ├─ class UserSchema
│  │  │  ├─ class ExamSchema
│  │  │  ├─ class TopicSchema
│  │  │  ├─ class QuestionSchema
│  │  │  ├─ class StudyPlanSchema
│  │  │  └─ ... all validation schemas
│  │  │
│  │  └─ repositories.py (Data access layer)
│  │     ├─ class BaseRepository
│  │     ├─ class UserRepository
│  │     ├─ class ExamRepository
│  │     ├─ class TopicRepository
│  │     ├─ class QuestionRepository
│  │     └─ ... CRUD operations
│  │
│  ├─ config/
│  │  ├─ __init__.py
│  │  ├─ settings.py
│  │  │  ├─ class Settings (Pydantic settings)
│  │  │  ├─ DATABASE_URL
│  │  │  ├─ REDIS_URL
│  │  │  ├─ LOG_LEVEL
│  │  │  ├─ SECRET_KEY
│  │  │  ├─ ENVIRONMENT (dev/test/prod)
│  │  │  ├─ API_VERSION
│  │  │  └─ ... all configuration
│  │  │
│  │  └─ constants.py
│  │     ├─ MAX_FILE_SIZE
│  │     ├─ ALLOWED_EXTENSIONS
│  │     ├─ DEFAULT_PAGE_SIZE
│  │     ├─ CACHE_TTL
│  │     └─ ... all constants
│  │
│  ├─ logging/
│  │  ├─ __init__.py
│  │  ├─ logger.py
│  │  │  ├─ def setup_logging()
│  │  │  ├─ class StructuredLogger
│  │  │  └─ get_logger(name)
│  │  │
│  │  └─ formatters.py
│  │     ├─ class JsonFormatter
│  │     └─ class StructuredFormatter
│  │
│  ├─ exceptions/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  │  ├─ class ExamVerseException (base)
│  │  │  ├─ class ValidationException
│  │  │  ├─ class NotFoundException
│  │  │  ├─ class UnauthorizedException
│  │  │  ├─ class ConflictException
│  │  │  ├─ class InternalServerException
│  │  │  └─ class RateLimitException
│  │  │
│  │  └─ handlers.py
│  │     ├─ def exception_handler(exc)
│  │     └─ def validation_error_handler(exc)
│  │
│  ├─ utils/
│  │  ├─ __init__.py
│  │  ├─ validators.py
│  │  │  ├─ def validate_email()
│  │  │  ├─ def validate_password()
│  │  │  ├─ def validate_url()
│  │  │  └─ ... validation functions
│  │  │
│  │  ├─ parsers.py
│  │  │  ├─ def parse_pdf_file()
│  │  │  ├─ def parse_text_file()
│  │  │  └─ ... parsing functions
│  │  │
│  │  ├─ helpers.py
│  │  │  ├─ def generate_uuid()
│  │  │  ├─ def format_datetime()
│  │  │  ├─ def paginate_results()
│  │  │  └─ ... helper functions
│  │  │
│  │  ├─ security.py (Phase 2)
│  │  │  ├─ def hash_password()
│  │  │  ├─ def verify_password()
│  │  │  ├─ def generate_jwt_token()
│  │  │  └─ def verify_jwt_token()
│  │  │
│  │  └─ cache.py
│  │     ├─ class CacheManager
│  │     ├─ def cache_key()
│  │     └─ ... caching utilities
│  │
│  ├─ enums/
│  │  ├─ __init__.py
│  │  ├─ exam_status.py
│  │  │  ├─ class ExamStatus (DRAFT, PUBLISHED, ARCHIVED)
│  │  │  ├─ class ExamType (COMPETITIVE, PRACTICE)
│  │  │  └─ ... exam enums
│  │  │
│  │  ├─ question_types.py
│  │  │  ├─ class QuestionType (MCQ, SHORT_ANSWER, ESSAY)
│  │  │  └─ ... question enums
│  │  │
│  │  ├─ user_roles.py
│  │  │  ├─ class UserRole (ADMIN, TEACHER, STUDENT)
│  │  │  └─ ... role enums
│  │  │
│  │  └─ study_status.py
│  │     ├─ class StudyStatus (NOT_STARTED, IN_PROGRESS, COMPLETED)
│  │     └─ ... study enums
│  │
│  └─ types/
│     ├─ __init__.py
│     └─ common.py
│        ├─ type Page (pagination)
│        ├─ type UUID
│        └─ ... custom types
│
├─ tests/
│  ├─ __init__.py
│  ├─ conftest.py (Pytest fixtures)
│  │  ├─ fixture db_session()
│  │  ├─ fixture sample_exam()
│  │  ├─ fixture sample_user()
│  │  └─ ... other fixtures
│  │
│  ├─ test_models.py
│  │  ├─ test_user_model_creation()
│  │  ├─ test_exam_model_validation()
│  │  ├─ test_topic_model_relationships()
│  │  └─ ... model tests
│  │
│  ├─ test_schemas.py
│  │  ├─ test_user_schema_validation()
│  │  ├─ test_exam_schema_required_fields()
│  │  └─ ... schema tests
│  │
│  ├─ test_repositories.py
│  │  ├─ test_user_repository_create()
│  │  ├─ test_exam_repository_query()
│  │  └─ ... repository tests
│  │
│  ├─ test_config.py
│  │  ├─ test_settings_load()
│  │  ├─ test_environment_override()
│  │  └─ ... config tests
│  │
│  └─ test_utils.py
│     ├─ test_validators()
│     ├─ test_helpers()
│     └─ ... utility tests
│
└─ .github/
   └─ workflows/ (Inherited from .github repo)
      ├─ tests.yml (Run pytest on PR)
      └─ publish.yml (Publish to PyPI)
```

---

## 🔗 How This Repo Connects to Others

### Connected to: **examverse-api**
```python
# In examverse-api code:
from examverse_core.database.models import User, Exam, Topic
from examverse_core.database.repositories import UserRepository
from examverse_core.config.settings import settings
from examverse_core.logging import get_logger
from examverse_core.exceptions import NotFoundException, ValidationException

# Use models
user = UserRepository(db_session).get_by_id(user_id)
# Use config
api_version = settings.API_VERSION
# Use logging
logger = get_logger(__name__)
```
- 📦 Imports: Models, schemas, repositories, config, logging, exceptions
- 🔄 How it's used: Every API endpoint uses core models & utilities
- 📝 When to update: When adding new database models or utility functions

### Connected to: **examverse-ingestion**
```python
# In examverse-ingestion code:
from examverse_core.database.models import Topic, Question
from examverse_core.config.settings import settings
from examverse_core.logging import get_logger
from examverse_core.utils.parsers import parse_pdf_file

# Parse documents
pdf_content = parse_pdf_file(file_path)
# Log operations
logger = get_logger(__name__)
# Access settings
max_file_size = settings.MAX_FILE_SIZE
```
- 📦 Imports: Models, parsers, config, logging
- 🔄 How it's used: Pipeline uses core models & utilities
- 📝 When to update: When adding new parser utilities

### Connected to: **examverse-db**
```
examverse-db/migrations/
    └─ Uses models from examverse-core
    └─ Creates database schema
    └─ Alembic references core models
```
- 📦 Imports: Database models from core
- 🔄 How it's used: Database migrations reference core models
- 📝 When to update: When updating database schema

### Connected to: **examverse-ai** (Phase 2+)
```python
# In examverse-ai code:
from examverse_core.database.models import Question, Topic
from examverse_core.database.repositories import QuestionRepository
from examverse_core.config.settings import settings

# Use AI-related repositories
questions = QuestionRepository(db_session).search_by_topic(topic_id)
```
- 📦 Imports: Models, repositories, config
- 🔄 How it's used: AI services use core models & database access
- 📝 When to update: When adding new model types

---

## 📦 What Goes In This Repo?

### ✅ PUT IT HERE:
- Database models (User, Exam, Topic, Question, etc.)
- Pydantic schemas for validation
- Data repositories (CRUD operations)
- Configuration management
- Logging setup
- Common exceptions
- Utility functions used by multiple services
- Constants and enums
- Security utilities (hashing, JWT, etc.)
- Caching utilities
- Validators and parsers

### ❌ DON'T PUT IT HERE:
- API endpoints (those go in examverse-api)
- Ingestion pipeline logic (that goes in examverse-ingestion)
- AI/ML models (those go in examverse-ai)
- Frontend code (that goes in examverse-web/admin)
- Deployment scripts (those go in examverse-devops)
- Service-specific business logic
- Service-specific configurations

---

## 🚀 How Services Use This Repo

### Step 1: Install examverse-core
```bash
# In examverse-api/requirements.txt:
examverse-core>=0.1.0

# Or install from local:
pip install -e ../examverse-core
```

### Step 2: Import what you need
```python
# models.py - Import database models
from examverse_core.database.models import (
    User, Exam, Topic, Question, StudyPlan
)

# schemas.py - Import validation schemas
from examverse_core.database.schemas import (
    UserSchema, ExamSchema, QuestionSchema
)

# config.py - Import settings
from examverse_core.config.settings import settings

# logging_setup.py - Import logger
from examverse_core.logging import get_logger
logger = get_logger(__name__)

# exception_handling.py - Import exceptions
from examverse_core.exceptions import (
    NotFoundException, ValidationException
)
```

### Step 3: Use in your service
```python
# In examverse-api/app/api/users.py:
from fastapi import APIRouter, HTTPException
from examverse_core.database.models import User
from examverse_core.database.repositories import UserRepository
from examverse_core.exceptions import NotFoundException

router = APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session):
    try:
        user = UserRepository(db).get_by_id(user_id)
        return user
    except NotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
```

---

## 🔄 Development Workflow

### When you need to add shared code:

**Step 1: Identify the need**
```
You're building examverse-api and realize:
"Multiple services will need to validate email addresses"
"Multiple services will need to cache results"
"I need a new database model"
```

**Step 2: Create in examverse-core**
```python
# In examverse-core/examverse_core/utils/validators.py:
def validate_email(email: str) -> bool:
    """Validate email format."""
    # validation logic
    return True

# In examverse-core/examverse_core/utils/cache.py:
class CacheManager:
    """Cache management utilities."""
    def get(self, key: str):
        pass
```

**Step 3: Test in examverse-core**
```bash
cd examverse-core
pytest tests/test_validators.py
pytest tests/test_cache.py
```

**Step 4: Increment version**
```python
# In examverse-core/__version__.py:
__version__ = "0.2.0"  # Was 0.1.0
```

**Step 5: Publish to PyPI**
```bash
# GitHub Actions publishes automatically on tag
git tag v0.2.0
git push origin v0.2.0
```

**Step 6: Update dependencies in other services**
```bash
# In examverse-api/requirements.txt:
examverse-core>=0.2.0  # Was >=0.1.0

# Install updated version
pip install --upgrade examverse-core
```

**Step 7: Use in your service**
```python
# In examverse-api code:
from examverse_core.utils.validators import validate_email
from examverse_core.utils.cache import CacheManager
```

---

## 📝 Installation & Usage

### For Development (Local)
```bash
# Clone and install in editable mode
git clone https://github.com/ExamVerseOS/examverse-core.git
cd examverse-core

# Install development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

### For Production (PyPI)
```bash
# Add to requirements.txt
examverse-core>=0.1.0

# Install
pip install -r requirements.txt
```

### Basic Usage
```python
# Import and use
from examverse_core.database.models import User
from examverse_core.config.settings import settings
from examverse_core.logging import get_logger

# Configure logging
logger = get_logger(__name__)
logger.info("Application started")

# Use settings
print(settings.DATABASE_URL)

# Use models
user = User(name="John", email="john@example.com")
```

---

## ✅ Testing

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_models.py
pytest tests/test_schemas.py
pytest tests/test_repositories.py
```

### Run with coverage
```bash
pytest --cov=examverse_core tests/
```

### Test database models
```bash
pytest tests/test_models.py -v
```

### Test validation schemas
```bash
pytest tests/test_schemas.py -v
```

### Test repositories (data access)
```bash
pytest tests/test_repositories.py -v
```

---

## 🎯 When to Create/Update Code Here

### CREATE new code in examverse-core when:
- [ ] Multiple services need the same functionality
- [ ] It's a database model needed by multiple services
- [ ] It's a utility function used by multiple services
- [ ] It's configuration that applies to multiple services
- [ ] It's a validation rule used by multiple services

### DON'T create code in examverse-core when:
- [ ] It's specific to one service (keep it in that service)
- [ ] It's a business workflow (keep it in that service)
- [ ] It's an API endpoint (keep it in examverse-api)
- [ ] It's a pipeline step (keep it in examverse-ingestion)
- [ ] It's an AI model (keep it in examverse-ai)

### Update examverse-core when:
- [ ] Adding new database models
- [ ] Adding new schemas for validation
- [ ] Adding new utility functions
- [ ] Fixing bugs in shared code
- [ ] Improving performance
- [ ] Adding new enums or constants

---

## 📋 Timeline

### ✅ Week 1 (Foundation)
- [x] Set up Python package structure
- [x] Create basic database models (User, Exam, Topic, Question)
- [x] Create Pydantic schemas for validation
- [x] Create repositories for CRUD operations
- [x] Set up logging
- [x] Create exception classes
- [x] Create utilities (validators, helpers)
- [x] Write tests for all code
- [x] Set up CI/CD for testing

### 🔄 Week 2 (Feature Development)
- [ ] Add new models as features are built (StudyPlan, etc.)
- [ ] Add new schemas for validation
- [ ] Add new repositories for data access
- [ ] Add new utilities as services need them
- [ ] Increment version (0.1.0 → 0.2.0)
- [ ] Publish to PyPI
- [ ] Update all services to use new version

### 🔄 Week 3+ (Ongoing)
- [ ] Maintain existing code
- [ ] Add new features as needed
- [ ] Fix bugs reported by services
- [ ] Improve performance
- [ ] Version increments as needed
- [ ] Regular PyPI updates

---

## 🔗 Related Repositories

| Repository | How it uses core | When to check |
|---|---|---|
| **examverse-api** | Imports models, schemas, repos | Every API feature |
| **examverse-ingestion** | Imports models, utilities | Every pipeline step |
| **examverse-db** | Uses models in migrations | Every schema change |
| **examverse-ai** | Imports models, repositories | AI feature development |
| **.github** | References version in workflows | Publishing to PyPI |

---

## 📊 Success Criteria

This repository is successful when:
- ✅ All shared code is here (no duplication across services)
- ✅ All services import from here successfully
- ✅ No circular dependencies
- ✅ All code has tests (>80% coverage)
- ✅ Version increments are clear
- ✅ PyPI publishing works
- ✅ All services can install and use latest version
- ✅ Documentation is current
- ✅ Breaking changes are documented
- ✅ New developers can understand what goes here

---

## 🤝 Contributing

### To add shared code:
1. Check if it's truly shared (used by multiple services)
2. Create code in appropriate module
3. Write tests for your code
4. Create PR with code + tests
5. Get code review
6. Merge to main
7. Version increment
8. Publish to PyPI
9. Update dependencies in other services

### Code standards:
- [ ] All code must have tests
- [ ] All code must have docstrings
- [ ] All code must follow PEP 8
- [ ] All tests must pass
- [ ] All code must have >80% test coverage

---

## 📞 Questions?

**Q: Should I put this in examverse-core?**  
A: Only if multiple services will use it. If it's specific to one service, keep it there.

**Q: How do I use a new version?**  
A: Update requirements.txt with new version, then `pip install --upgrade`.

**Q: Where do I report bugs?**  
A: Create an issue in this repo with details and stack trace.

**Q: How do I add a new database model?**  
A: Add to models.py, create schema, create repository, write tests, increment version.

**Q: What if I need something not in core?**  
A: Add it here if multiple services need it, otherwise keep it in your service.

---

## 📚 Related Documents

- [examverse-docs/ARCHITECTURE.md](https://github.com/ExamVerseOS/examverse-docs/blob/main/ARCHITECTURE.md) - System architecture
- [examverse-docs/DATABASE.md](https://github.com/ExamVerseOS/examverse-docs/blob/main/DATABASE.md) - Database schema
- [examverse-docs/API.md](https://github.com/ExamVerseOS/examverse-docs/blob/main/API.md) - API specification
- [examverse-db/README.md](https://github.com/ExamVerseOS/examverse-db) - Database migrations

---

**Last Updated:** 2024 (Week 1 - Foundation)  
**Next Review:** End of Week 2 (when services integrate)

---

*examverse-core is the shared foundation for all backend services. Keep it clean, focused, and well-tested.*
