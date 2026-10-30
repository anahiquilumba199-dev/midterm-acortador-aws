
import os
from uuid import uuid4

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

# Cargar configuracion
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "ShortLinks")
API_URL = os.getenv("PUBLIC_API_URL", "http://127.0.0.1:8000")

# Conexion con DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

# Crear API
app = FastAPI(title="Acortador de enlaces")

# Permitir conexion con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Datos que recibe la API
class LinkRequest(BaseModel):
    original_url: HttpUrl


# Comprobar que la API funciona
@app.get("/health")
def health():
    return {"mensaje": "API funcionando correctamente"}


# Crear un enlace corto
@app.post("/shorten")
def create_link(data: LinkRequest):

    code = str(uuid4())[:8]
    original_url = str(data.original_url)

    link = {
        "short_code": code,
        "original_url": original_url
    }

    try:
        table.put_item(Item=link)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al guardar el enlace"
        )

    return {
        "short_code": code,
        "original_url": original_url,
        "short_url": f"{API_URL}/{code}"
    }


# Consultar un enlace
@app.get("/urls/{code}")
def get_link(code: str):

    try:
        result = table.get_item(Key={"short_code": code})
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar el enlace"
        )

    if "Item" not in result:
        raise HTTPException(
            status_code=404,
            detail="Enlace no encontrado"
        )

    return result["Item"]


# Redireccionar al enlace original
@app.get("/{code}")
def redirect_link(code: str):

    try:
        result = table.get_item(Key={"short_code": code})
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar el enlace"
        )

    if "Item" not in result:
        raise HTTPException(
            status_code=404,
            detail="Enlace no encontrado"
        )

    return RedirectResponse(
        url=result["Item"]["original_url"]
    )
