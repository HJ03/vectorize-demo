from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import uuid
import os

from app.vectorize import image_to_vector


app = FastAPI()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
STATIC_DIR = os.path.join(ROOT_DIR, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/", response_class=HTMLResponse)
def home():
    with open(os.path.join(STATIC_DIR, "index.html")) as f:
        return f.read()

@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{uid}_{file.filename}")
    dxf_path = os.path.join(OUTPUT_DIR, f"{uid}.dxf")
    svg_path = os.path.join(OUTPUT_DIR, f"{uid}.svg")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_to_vector(input_path, dxf_path, svg_path)

    return {
        "svg_url": f"/outputs/{uid}.svg",
        "dxf_url": f"/outputs/{uid}.dxf"
    }
