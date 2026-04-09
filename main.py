from __future__ import annotations

import io
import json
import re
import uuid
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PACKING_FILE = BASE_DIR / "packing.json"

app = FastAPI(title="ASN Tool GM")

app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR))


def norm_rev(value):
    text = str(value or "0").strip() or "0"
    digits = re.sub(r"\D", "", text)
    return f"{int(digits or '0'):02d}"


class PackingStore:
    @staticmethod
    def ensure_seed():
        if PACKING_FILE.exists():
            return
        data = {"single": [], "pair": []}
        PACKING_FILE.write_text(json.dumps(data), encoding="utf-8")

    @staticmethod
    def load():
        PackingStore.ensure_seed()
        return json.loads(PACKING_FILE.read_text(encoding="utf-8"))

    @staticmethod
    def save(data):
        PACKING_FILE.write_text(json.dumps(data), encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/manifest.json")
async def manifest():
    return FileResponse(BASE_DIR / "manifest.json")


@app.get("/service-worker.js")
async def sw():
    return FileResponse(BASE_DIR / "service-worker.js")


@app.get("/health")
async def health():
    return {"ok": True}
