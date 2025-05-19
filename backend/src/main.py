from fastapi import FastAPI, Request, Security, status
import uvicorn

app = FastAPI(root_path='/api')

@app.get("/")
async def root():
    return "test 345"
