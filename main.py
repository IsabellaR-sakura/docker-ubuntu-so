from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
import boto3
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

app = FastAPI(title="Taller AWS - Sistemas Operativos")

# --- CONFIGURACIONES CLAVE ---
BUCKET_NAME = "user-20052026-ueia-so" 
DATABASE_URL = "mysql+pymysql://admin:TU_PASSWORD@TU_RDS_ENDPOINT:3306/nombre_bd"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definición del esquema de la tabla en RDS
class RegistroImagen(Base):
    __tablename__ = "registro_imagenes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String(100), index=True)
    ruta_s3 = Column(String(255))
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)

# Generar automáticamente la estructura de la tabla al iniciar la app
Base.metadata.create_all(bind=engine)

s3_client = boto3.client('s3')

# --- ENDPOINTS REQUERIDOS ---

# a. Endpoint POST para cargar la imagen organizando por usuario
@app.post("/upload")
async def upload_image(usuario: str = Form(...), file: UploadFile = File(...)):
    # Validación estricta del tipo de formato recibido
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato inválido. Solo se permite cargar archivos PNG o JPG/JPEG."
        )
    
    # Construcción de la ruta: usuarios/nombre_usuario/fecha_archivo.ext
    extension = file.filename.split(".")[-1]
    marca_tiempo = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    ruta_s3_destino = f"usuarios/{usuario}/{marca_tiempo}.{extension}"
    
    try:
        # Cargar directamente el stream del archivo subido a Amazon S3
        s3_client.upload_fileobj(file.file, BUCKET_NAME, ruta_s3_destino)
        
        # Guardar metadatos en la base de datos relacional RDS
        db = SessionLocal()
        nuevo_registro = RegistroImagen(usuario=usuario, ruta_s3=ruta_s3_destino)
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)
        db.close()
        
        return {
            "status": "Éxito",
            "mensaje": "Imagen procesada y persistida de forma correcta",
            "datos_registro": {
                "id": nuevo_registro.id,
                "usuario": nuevo_registro.usuario,
                "ruta_s3": nuevo_registro.ruta_s3,
                "fecha_creacion": nuevo_registro.fecha_creacion
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo crítico en servidores AWS: {str(e)}")

# b. Endpoint GET para consultar y generar URL temporal prefirmada
@app.get("/image/{usuario}/{nombre_imagen}")
async def get_image(usuario: str, nombre_imagen: str):
    db = SessionLocal()
    # Reconstrucción del Key exacto guardado en el bucket
    ruta_esperada = f"usuarios/{usuario}/{nombre_imagen}"
    
    registro = db.query(RegistroImagen).filter(
        RegistroImagen.usuario == usuario,
        RegistroImagen.ruta_s3 == ruta_esperada
    ).first()
    db.close()
    
    # Validación de existencia de datos
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario o la imagen solicitada no existen en los registros del sistema."
        )
    
    try:
        # Firma digital temporal de AWS para otorgar acceso privado por 60 minutos
        url_segura = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': registro.ruta_s3},
            ExpiresIn=3600
        )
        return {
            "usuario": registro.usuario,
            "ruta_s3": registro.ruta_s3,
            "url_acceso_prefirmada": url_segura,
            "fecha_almacenamiento_rds": registro.fecha_creacion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar enlace seguro: {str(e)}")
