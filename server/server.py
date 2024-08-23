from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
import uvicorn
import requests
import os
import base64
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
    download_zip: str
    checksum_zip: str

@api.get("/check-version")
def check_version():
    release = get_latest_release()
    version = release.get("tag_name")
    
    if not version:
        raise HTTPException(status_code=404, detail="Version information not found")

    return {"version": version}

@api.get("/get-update", response_model=VersionInfo)
async def check_update(os_version: str = Query(..., description="OS version to fetch update for")):
    release = get_latest_release()
    version = release.get("tag_name")
    assets = release.get("assets", [])
    
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found for the release")
    
    zip_file_url = None
    checksum_url = None
    
    for asset in assets:
        if os_version in asset["name"] and asset["name"].endswith(".zip"):
            zip_file_url = asset["url"]
            
            # Generate checksum URL
            checksum_name = asset["name"] + ".sha256"
            checksum_url = next((a["url"] for a in assets if a["name"] == checksum_name), None)
            
            if checksum_url is None:
                raise HTTPException(status_code=404, detail=f"Checksum file for {asset['name']} not found")
            
            break
    
    if not zip_file_url:
        raise HTTPException(status_code=404, detail=f"No update found for OS version '{os_version}'")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/octet-stream"
    }
    
    # Fetch the zip file and checksum file
    zip_response = requests.get(zip_file_url, headers=headers)
    if zip_response.status_code != 200:
        raise HTTPException(status_code=zip_response.status_code, detail="Failed to download update file")
    
    checksum_response = requests.get(checksum_url, headers=headers)
    if checksum_response.status_code != 200:
        raise HTTPException(status_code=checksum_response.status_code, detail="Failed to download checksum file")

    # Encode files as base64
    download_zip_base64 = base64.b64encode(zip_response.content).decode('utf-8')
    checksum_zip_base64 = base64.b64encode(checksum_response.content).decode('utf-8')

    return VersionInfo(
        version=version,
        download_zip=download_zip_base64,
        checksum_zip=checksum_zip_base64
    )

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
