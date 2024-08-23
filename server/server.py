from fastapi import FastAPI, HTTPException, Query, Response
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
    checksum_url: str

@api.get("/check-version")
def check_version():
    release = get_latest_release()
    version = release.get("tag_name")
    
    if not version:
        raise HTTPException(status_code=404, detail="Version information not found")

    return {"version": version}

@api.get("/get-update")
def check_update(os_version: str = Query(..., description="OS version to fetch update for")):
    release = get_latest_release()
    version = release.get("tag_name")
    assets = release.get("assets", [])
    
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found for the release")
    
    download_url = None
    checksum_url = None
    
    for asset in assets:
        if os_version in asset["name"] and asset["name"].endswith(".zip"):
            download_url = asset["browser_download_url"]
            
            # Generate checksum URL
            checksum_name = asset["name"] + ".sha256"
            checksum_url = next((a["browser_download_url"] for a in assets if a["name"] == checksum_name), None)
            
            if checksum_url is None:
                raise HTTPException(status_code=404, detail=f"Checksum file for {asset['name']} not found")
            
            break
    
    if not download_url:
        raise HTTPException(status_code=404, detail=f"No update found for OS version '{os_version}'")
    
    return VersionInfo(
        version=version,
        download_url=download_url,
        checksum_url=checksum_url
    )

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
