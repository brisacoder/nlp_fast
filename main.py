from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
import secrets
from pathlib import Path
import csv
import json
from datetime import datetime

# Authentication
security = HTTPBasic()
USERNAME = "user"
PASSWORD = "pass"

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

app = FastAPI()

# Add session middleware for user-specific data
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Removed global uploaded_file_path - now using sessions

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, credentials: HTTPBasicCredentials = Depends(authenticate)):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), credentials: HTTPBasicCredentials = Depends(authenticate)):
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    content = await file.read()
    # Check file size limit (100MB)
    max_size = 100 * 1024 * 1024  # 100MB in bytes
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB")
    # Create uploads directory if not exists
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    # Save with original filename
    original_name = Path(file.filename).name
    file_path = uploads_dir / original_name
    with open(file_path, "wb") as f:
        f.write(content)
    # Store file path in user's session
    request.session["uploaded_file_path"] = str(file_path)
    # Process the file
    process_csv(file_path)
    return {"message": f"File {original_name} uploaded and processed"}

def process_csv(file_path: Path):
    # Placeholder for processing
    print(f"Processing {file_path}")
    # For example, read CSV
    with open(file_path, 'r') as f:
        reader = csv.reader(f)


@app.post("/ask")
async def ask_question(request: Request, question: str = Form(...), credentials: HTTPBasicCredentials = Depends(authenticate)):
    uploaded_file_path_str = request.session.get("uploaded_file_path")
    if not uploaded_file_path_str:
        raise HTTPException(status_code=400, detail="No file uploaded")
    uploaded_file_path = Path(uploaded_file_path_str)
    response = process_question(question, uploaded_file_path)
    # Save Q&A to log
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": uploaded_file_path.name,
        "question": question,
        "answer": response
    }
    with open(uploads_dir / "qa_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return {"response": response}

def process_question(question: str, file_path: Path):
    # Placeholder
    return f"Answer to: {question} based on {file_path}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
