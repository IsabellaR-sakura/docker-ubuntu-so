from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from mangum import Mangum
import boto3
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

app = FastAPI(title="Taller AWS")

BUCKET_NAME = "user-10203040-ueia-so"

DATABASE_URL = "sqlite:////tmp/test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class RegistroImagen(Base):
    __tablename__ = "imagenes"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(100))
    ruta_s3 = Column(String(255))
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

s3_client = boto3.client("s3")

@app.get("/")
def home():
    return {"mensaje": "API funcionando correctamente"}

@app.post("/upload")
async def upload_image(
    usuario: str = Form(...),
    file: UploadFile = File(...)
):

    if file.content_type not in [
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato inválido"
        )

    extension = file.filename.split(".")[-1]

    nombre = datetime.datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    ruta_s3 = f"usuarios/{usuario}/{nombre}.{extension}"

    try:

        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            ruta_s3
        )

        db = SessionLocal()

        nuevo = RegistroImagen(
            usuario=usuario,
            ruta_s3=ruta_s3
        )

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        db.close()

        return {
            "mensaje": "Imagen subida correctamente",
            "ruta": ruta_s3
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/image/{usuario}/{nombre}")
async def get_image(usuario: str, nombre: str):

    ruta = f"usuarios/{usuario}/{nombre}"

    db = SessionLocal()

    registro = db.query(RegistroImagen).filter(
        RegistroImagen.usuario == usuario,
        RegistroImagen.ruta_s3 == ruta
    ).first()

    db.close()

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="Imagen no encontrada"
        )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": registro.ruta_s3
        },
        ExpiresIn=3600
    )

    return {
        "url": url
    }

handler = Mangum(app)
