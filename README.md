# BookMind

An intelligent document processing and AI chat application built with FastAPI. Users can upload PDF/text files for content extraction and interact with an AI assistant powered by Groq's LLaMA model.

## 🚀 Features

- **User Authentication**: Complete auth system with JWT tokens
  - User registration and login
  - Password hashing with bcrypt
  - Forgot/reset password functionality
  - Profile management (update/delete)

- **File Processing**: Upload and parse documents
  - PDF text extraction
  - Text file processing
  - Content extraction for AI context

- **AI Chat**: Intelligent assistant powered by Groq LLaMA
  - Context-aware responses
  - Document Q&A capability
  - Clear and precise answers

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Groq API key (for AI features)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jacobgokul/BookMind.git
   cd BookMind
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   source env/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Create a database named `bookmind_db`
   - Update credentials in `database/database.py`

5. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   groq_api_key=your_groq_api_key_here
   ```

## 🚦 Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### User Management (`/user`)
- `POST /user/register` - Register new user
- `POST /user/login` - Login and get JWT token
- `POST /user/forgot_password` - Request password reset
- `POST /user/reset_password` - Reset password with token
- `PUT /user/update_profile` - Update user profile (requires auth)
- `DELETE /user/delete_profile` - Delete user account (requires auth)

### File Processing (`/genric`)
- `POST /genric/upload_file` - Upload and parse PDF/text files

### AI Services (`/ai`)
- `GET /ai/chat?user_query=<your_question>` - Chat with AI assistant

## 🗂️ Project Structure

```
BookMind/
├── main.py                 # Application entry point
├── database/
│   ├── database.py        # Database connection setup
│   └── models.py          # SQLAlchemy ORM models
├── routers/
│   ├── user_service.py    # User authentication endpoints
│   ├── genric_services.py # File upload endpoints
│   └── ai_services.py     # AI chat endpoints
├── schemas/
│   └── user_schema.py     # Pydantic validation schemas
├── utils/
│   ├── auth_utils.py      # JWT & password hashing utilities
│   └── parser.py          # File parsing utilities
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🔐 Authentication

Protected endpoints require a Bearer token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

Get token by calling `/user/login` with valid credentials.

## 💡 Usage Example

```python
import requests

# 1. Register user
response = requests.post("http://localhost:8000/user/register", json={
    "user_name": "John Doe",
    "email": "john@example.com",
    "password": "secure_password"
})

# 2. Login
response = requests.post("http://localhost:8000/user/login", json={
    "email": "john@example.com",
    "password": "secure_password"
})
token = response.json()["access_token"]

# 3. Upload file
files = {"file": open("document.pdf", "rb")}
response = requests.post("http://localhost:8000/genric/upload_file", files=files)
content = response.json()

# 4. Chat with AI
response = requests.get("http://localhost:8000/ai/chat", params={
    "user_query": "Summarize the document"
})
```

## 🔧 Configuration

### Database Settings (`database/database.py`)
```python
username = "postgres"
password = "your_password"
db_name = "bookmind_db"
ip_address = "localhost"
port = 5432
```

### JWT Settings (`utils/auth_utils.py`)
```python
SECRET_KEY = "YOUR_SECRET_KEY"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 3
```

## 📝 TODO

- **API Enhancements**
  - [ ] Chat history tracking
  - [ ] User conversation management
  - [ ] Document storage and retrieval

- **AI Improvements**
  - [ ] Multi-document support

- **Security**
  - [ ] Move secrets to environment variables
  - [ ] Add rate limiting
  - [ ] Implement refresh tokens

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Jacob Gokul**
- GitHub: [@Jacobgokul](https://github.com/Jacobgokul)
