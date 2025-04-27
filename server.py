from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Turkanime Downloader API is running."}

@app.get("/download")
def download_anime(anime_name: str):
    try:
        # Call your script (assume it's main.py and accepts anime name)
        result = subprocess.run(["python", "main.py", anime_name], capture_output=True, text=True)
        return {"output": result.stdout}
    except Exception as e:
        return {"error": str(e)}
