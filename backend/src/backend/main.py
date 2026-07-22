from fastapi import FastAPI

app = FastAPI(
    version="1.0.0",
    redirect_slashes=False,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)