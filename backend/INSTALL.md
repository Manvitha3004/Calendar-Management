# Installation Instructions

1. First, activate your virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

2. Install motor and other required packages:
```bash
pip install motor
pip install "fastapi[all]"
pip install python-dotenv
pip install uvicorn
```

3. If you haven't installed MongoDB, download and install it from:
https://www.mongodb.com/try/download/community

4. Start MongoDB service (if not already running)
- Windows: MongoDB runs as a service by default
- Unix/MacOS: `mongod --dbpath /path/to/data/db`

5. Create a .env file with:
```
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=calendar_app
```

6. Run the FastAPI application:
```bash
uvicorn main:app --reload
```