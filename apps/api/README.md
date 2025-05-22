# API (Python Backend)

This is the Python backend for the monorepo. You can use any Python web framework (e.g., FastAPI, Flask).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```

## Example FastAPI app

Create a file named `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Run the server

```bash
uvicorn main:app --reload
```
