from fastapi import FastAPI, Query, File, UploadFile,Form,HTTPException
from pydantic import BaseModel,Field, field_validator, computed_field
from typing import Dict, Annotated, Literal, Union, List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import time
import os
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import json
import random
import requests
import uuid
import numpy as np
pwd = os.getcwd()
app = FastAPI()
def extractConfig(nameModel="SystemData",relPath=os.path.join(pwd,"conf/experiment_config.json"),dataOut="keyantrophics"):
    configPath=os.path.join(os.getcwd(),relPath)
    with open(configPath, 'r', encoding='utf-8') as file:
        config = json.load(file)[nameModel]
    Output= config[dataOut]
    return Output
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configurar templates (para archivos HTML externos)
templates = Jinja2Templates(directory="templates")

# Configurar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def root():
    return {"message": "Welcome to the FastAPI server!"}

