from fastapi import FastAPI, HTTPException, Response, responses
from pydantic import BaseModel
import uvicorn
import os

api = FastAPI()


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

    return responses.HTMLResponse(content=body)

@api.get("/api/health_check")
def health_check():
    try:
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unhealthy: " + str(e))
    
LATEST_VERSION = "v1.0"
UPDATE_FILES_PATH = "/path/to/your/updates"
VERSION_INFO = {
    "version": LATEST_VERSION,
    "download_url": f"/download/{LATEST_VERSION}",
    "checksum": "expected_checksum_value"  # Replace with actual checksum
}

# Model for version info response
class VersionInfo(BaseModel):
    version: str
    download_url: str
    checksum: str

@api.get("/check-update", response_model=VersionInfo)
def check_update():
    # Respond with the latest version info
    return VERSION_INFO

@api.get("/download/{version}")
def download_update(version: str):
    file_path = os.path.join(UPDATE_FILES_PATH, f"{version}.zip")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Update not found")

    return Response(
        content=open(file_path, "rb").read(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={version}.zip"}
    )
    
uvicorn.run(api, host="0.0.0.0", port=8000)