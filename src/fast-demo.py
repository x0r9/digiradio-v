from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import json

#Local modules
import aprs_data

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def get_config(config_path="config.json"):
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            return json.loads(f.read())
    raise IOError("No config file found")

config = get_config()

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

@app.get("/last-points/{window_secs}")
async def last_points(request: Request, window_secs: int):
    return {"points":aprs_data.get_last_points(window_secs)}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("full-map.html", {"request": request, "config":config})
    return {"message": "Hello World"}

