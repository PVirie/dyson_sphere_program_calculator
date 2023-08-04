from fastapi import APIRouter, FastAPI, Depends, HTTPException, Header, Query, Body, status, Response, Form, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@ app.on_event("startup")
async def startup_event():
    print("Test is starting up.")


@ app.on_event("shutdown")
def shutdown_event():
    print("Test is exiting.", "Wait a moment until completely exits.")

app.mount("/", StaticFiles(directory="."))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("mock_server:app", host="127.0.0.1",
                port=8000, log_level="info")
