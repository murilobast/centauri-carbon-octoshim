import os
import hashlib
import uuid
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException

PRINTER_IP = os.environ.get("PRINTER_IP", "").strip()
if not PRINTER_IP:
    raise RuntimeError("Defina PRINTER_IP no docker-compose.yml")

# We "pretend" to be OctoPrint >= 1.1
OCTO_VERSION = "1.10.0"   # you can change to "1.9.3" etc; 1.10.0 is fine

app = FastAPI()

@app.get("/api/version")
def api_version():
    # Some clients check that the text contains "OctoPrint"
    return {"api": "0.1", "server": OCTO_VERSION, "text": f"OctoPrint {OCTO_VERSION}"}

@app.get("/api/server")
def api_server():
    # Some clients call this instead of /api/version
    return {"server": OCTO_VERSION, "safemode": None}

@app.get("/api/settings")
def api_settings():
    # Some slicers test this endpoint. Minimal response.
    return {"api": {"enabled": True}, "appearance": {}, "feature": {}, "plugins": {}}

@app.get("/api/printer")
def api_printer():
    # Minimal response so the "probe" doesn't fail
    return {"state": {"text": "Operational", "flags": {"operational": True, "printing": False}}}

@app.get("/api/connection")
def api_connection():
    return {"current": {"state": "Operational"}, "options": {}}

@app.post("/api/files/{location}")
async def upload_file(
    location: str,
    file: UploadFile = File(...),
    select: str | None = Form(default=None),
    print_: str | None = Form(default=None, alias="print"),
):
    if location not in ("local", "sdcard"):
        raise HTTPException(status_code=400, detail="Unsupported location")

    filename = file.filename or "upload.gcode"
    data = await file.read()

    md5 = hashlib.md5(data).hexdigest()
    transfer_uuid = uuid.uuid4().hex

    url = f"http://{PRINTER_IP}:3030/uploadFile/upload"
    form = {
        "TotalSize": str(len(data)),
        "Uuid": transfer_uuid,
        "Offset": "0",
        "Check": "1",
        "S-File-MD5": md5,
    }
    files = {"File": (filename, data, "application/octet-stream")}

    r = requests.post(url, data=form, files=files, timeout=120)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Printer upload HTTP {r.status_code}")

    try:
        j = r.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Printer upload returned non-JSON")

    if not j.get("success", False):
        raise HTTPException(status_code=502, detail=f"Printer upload failed: {j}")
