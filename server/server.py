from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import uvicorn
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api = FastAPI()

# Get GitHub repository details from environment variables
GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_latest_release():
    url = GITHUB_API_URL.format(owner=OWNER, repo=REPO)
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="GitHub API request failed")

    return response.json()

@api.get('/')
def index():
    body = (
        '<html>'
        "<body style='padding: 10px;'>"
        '<h1>Welcome to the Non-Trivial-API</h1>'
        '<div>'
        "Try it: <a href='/api/health_check'>/api/health_check</a>"
        '</div>'
        '</body>'
        '</html>'
    )
    return Response(content=body, media_type="text/html")

@api.get("/api/health_check")
def health_check():
    try:
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unhealthy: " + str(e))

# Model for version info response
class VersionInfo(BaseModel):
    version: str
    download_url: str
    checksum: str  # This should be computed or fetched from the release

@api.get("/check-update", response_model=VersionInfo)
def check_update():
    release = get_latest_release()
    version = release.get("tag_name")
    assets = release.get("assets", [])
    download_url = None
    checksum = None
    
    for asset in assets:
        if asset["name"].endswith(".zip"):
            download_url = asset["browser_download_url"]
            checksum = asset.get("checksum", "N/A")  # Adjust this if your assets have a checksum field
            
    if not download_url:
        raise HTTPException(status_code=404, detail="Update not found")
    
    return VersionInfo(
        version=version,
        download_url=download_url,
        checksum=checksum
    )

@api.get("/download/{os_version}")
def download_update(os_version: str):
    release = get_latest_release()
    version = release.get("tag_name")
    assets = release.get("assets", [])
    download_url = None
    
    for asset in assets:
        if os_version in asset["name"] and asset["name"].endswith(".zip"):
            download_url = asset["browser_download_url"]
            break

    if not download_url:
        raise HTTPException(status_code=404, detail="Update not found")

    response = requests.get(download_url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to download update")

    return Response(
        content=response.content,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={version}.zip"}
    )

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
