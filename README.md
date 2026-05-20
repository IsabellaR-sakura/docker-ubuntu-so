# Taller AWS - S3, EC2, Docker y Lambda

Proyecto desarrollado para el taller de Sistemas Operativos utilizando servicios de AWS: Amazon S3, EC2, ECR y AWS Lambda con FastAPI y Docker.

---

# 📁 Estructura del Proyecto

```plaintext
Taller_AWS/
│
├── archivo1.txt
├── s3_test.py
├── descargas_cli/
├── descargas_boto3/
│
└── mi_proyecto_fastapi/
    ├── main.py
    ├── Dockerfile
    ├── requirements.txt
    ├── README.md
    └── evidencias/
```

---

# 1. CONFIGURACIÓN INICIAL

## 1.1 Crear carpeta principal del taller

Abrir terminal Ubuntu y ejecutar:

```bash
cd ~

mkdir Taller_AWS

cd Taller_AWS
```

Ruta actual:

```plaintext
~/Taller_AWS
```

---

# 2. AMAZON S3

# 2.1 Crear Bucket S3

Desde la terminal:

```bash
aws s3api create-bucket \
--bucket user-10203040-ueia-so \
--region us-east-1
```

IMPORTANTE:

Cambiar:

```plaintext
10203040
```

por tu documento o identificador único.

---

# 📸 Evidencia 1

Captura de:

- comando ejecutado
- respuesta JSON de AWS

---

# 2.2 Crear archivo local

Seguimos en:

```plaintext
~/Taller_AWS
```

Crear archivo:

```bash
echo "Hola AWS" > archivo1.txt
```

Verificar:

```bash
ls
```

---

# 2.3 Subir archivo a S3 usando AWS CLI

```bash
aws s3 cp archivo1.txt s3://user-10203040-ueia-so/archivo1.txt
```

---

# 2.4 Verificar contenido del bucket

```bash
aws s3 ls s3://user-10203040-ueia-so/
```

---

# 📸 Evidencia 2

Captura de:

- comando `aws s3 ls`
- archivo listado en el bucket

---

# 2.5 Descargar archivo desde S3

Crear carpeta:

```bash
mkdir descargas_cli
```

Descargar:

```bash
aws s3 cp \
s3://user-10203040-ueia-so/archivo1.txt \
./descargas_cli/archivo1.txt
```

Entrar a la carpeta:

```bash
cd descargas_cli
```

Verificar:

```bash
ls -l
```

---

# 📸 Evidencia 3

Captura de:

- terminal mostrando el archivo descargado

---

# 2.6 Volver a carpeta principal

```bash
cd ..
```

Ruta actual:

```plaintext
~/Taller_AWS
```

---

# 3. SCRIPT PYTHON CON BOTO3

# 3.1 Instalar boto3

```bash
pip install boto3
```

o:

```bash
python3 -m pip install boto3
```

---

# 3.2 Crear script

Desde:

```plaintext
~/Taller_AWS
```

Crear archivo:

```bash
nano s3_test.py
```

Pegar:

```python
import os
import boto3

s3 = boto3.client('s3')

BUCKET_NAME = 'user-10203040-ueia-so'

# Subir archivo individual
s3.upload_file(
    'archivo1.txt',
    BUCKET_NAME,
    'boto3_archivo1.txt'
)

print("[OK] Archivo individual cargado.")

# Crear carpeta de descargas
os.makedirs('descargas_boto3', exist_ok=True)

# Descargar archivo
s3.download_file(
    BUCKET_NAME,
    'boto3_archivo1.txt',
    'descargas_boto3/boto3_archivo1.txt'
)

print("[OK] Archivo descargado.")

# Archivos múltiples
archivos = ['test1.txt', 'test2.txt', 'test3.txt']

for a in archivos:
    with open(a, 'w') as f:
        f.write(f"Contenido de {a}")

# Subida múltiple
for a in archivos:
    s3.upload_file(
        a,
        BUCKET_NAME,
        f"multi/{a}"
    )

print("[OK] Archivos múltiples cargados.")

# Descarga múltiple
for a in archivos:
    s3.download_file(
        BUCKET_NAME,
        f"multi/{a}",
        f"descargas_boto3/{a}"
    )

print("[OK] Archivos múltiples descargados.")
```

Guardar:

```plaintext
CTRL + O
ENTER
CTRL + X
```

---

# 3.3 Ejecutar script

```bash
python3 s3_test.py
```

---

# 📸 Evidencia 4

Captura de:

- mensajes `[OK]`
- ejecución exitosa

---

# 4. CREAR PROYECTO FASTAPI

# 4.1 Crear carpeta del proyecto

Desde:

```plaintext
~/Taller_AWS
```

Ejecutar:

```bash
mkdir mi_proyecto_fastapi

cd mi_proyecto_fastapi
```

Ruta actual:

```plaintext
~/Taller_AWS/mi_proyecto_fastapi
```

---

# 4.2 Crear requirements.txt

```bash
nano requirements.txt
```

Pegar:

```plaintext
fastapi==0.110.0
uvicorn==0.28.0
boto3==1.34.0
sqlalchemy==2.0.28
pymysql==1.1.0
cryptography==42.0.5
python-multipart==0.0.9
mangum==0.17.0
```

Guardar y salir.

---

# 4.3 Crear main.py

```bash
nano main.py
```

Pegar:

```python
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
```

Guardar y salir.

---

# 4.4 Crear Dockerfile

```bash
nano Dockerfile
```

Pegar:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Guardar y salir.

---

# 5. GITHUB

# 5.1 Inicializar repositorio

Seguimos en:

```plaintext
~/Taller_AWS/mi_proyecto_fastapi
```

Ejecutar:

```bash
git init

git add .

git commit -m "Primer commit"
```

---

# 5.2 Conectar repositorio remoto

```bash
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
```

---

# 5.3 Subir proyecto

```bash
git branch -M main

git push -u origin main
```

Si pide usuario:

```plaintext
TU USUARIO GITHUB
```

Si pide password:

```plaintext
TOKEN PERSONAL DE GITHUB
```

NO la contraseña normal.

---

# 📸 Evidencia 5

Captura del repositorio GitHub con:

- main.py
- Dockerfile
- requirements.txt

---

# 6. CREAR INSTANCIA EC2

# 6.1 Crear instancia

En AWS:

```plaintext
EC2 → Launch Instance
```

Configuración:

## Nombre

```plaintext
Servidor-FastAPI-SO
```

## Sistema operativo

```plaintext
Ubuntu 22.04 LTS
```

## Tipo

```plaintext
t2.micro
```

## Key Pair

Crear:

```plaintext
llave-taller.pem
```

Guardar el `.pem` en:

```plaintext
~/Taller_AWS
```

---

# 6.2 Abrir puertos

En:

```plaintext
Security Groups → Edit inbound rules
```

Agregar:

| Tipo | Puerto | Source |
|---|---|---|
| SSH | 22 | Anywhere |
| Custom TCP | 8000 | Anywhere |
| Custom TCP | 8080 | Anywhere |

Guardar reglas.

---

# 📸 Evidencia 6

Captura de:

- inbound rules
- puertos 8000 y 8080 abiertos

---

# 6.3 Conectarse por SSH

Desde:

```plaintext
~/Taller_AWS
```

Ejecutar:

```bash
chmod 400 llave-taller.pem
```

Conectarse:

```bash
ssh -i "llave-taller.pem" ubuntu@IP_PUBLICA
```

---

# 7. CONFIGURAR EC2

Ahora estás dentro de AWS EC2.

Ruta:

```plaintext
/home/ubuntu
```

---

# 7.1 Actualizar Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
```

---

# 7.2 Instalar herramientas

```bash
sudo apt install python3-pip python3-venv git docker.io -y
```

---

# 7.3 Clonar repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git app
```

Entrar:

```bash
cd app
```

Ruta actual:

```plaintext
/home/ubuntu/app
```

---

# 7.4 Crear entorno virtual

```bash
python3 -m venv venv
```

Activar:

```bash
source venv/bin/activate
```

---

# 7.5 Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# 7.6 Ejecutar FastAPI

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Abrir en navegador:

```plaintext
http://IP_PUBLICA:8000/docs
```

---

# 📸 Evidencia 7

Captura de Swagger funcionando.

---

# 8. CONFIGURAR SYSTEMD

Crear servicio:

```bash
sudo nano /etc/systemd/system/fastapi.service
```

Pegar:

```ini
[Unit]
Description=FastAPI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/app
ExecStart=/home/ubuntu/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Guardar.

---

# 8.1 Activar servicio

```bash
sudo systemctl daemon-reload

sudo systemctl start fastapi

sudo systemctl enable fastapi
```

Verificar:

```bash
sudo systemctl status fastapi
```

---

# 📸 Evidencia 8

Captura de:

```plaintext
active (running)
```

---

# 9. DOCKER

# 9.1 Construir imagen

Salir de EC2:

```bash
exit
```

Volvemos a local.

Entrar al proyecto:

```bash
cd ~/Taller_AWS/mi_proyecto_fastapi
```

Construir:

```bash
docker build -t fastapi-aws-taller .
```

---

# 9.2 Ejecutar contenedor

```bash
docker run -d -p 8080:8080 --name app_taller fastapi-aws-taller
```

Verificar:

```bash
docker ps
```

---

# 📸 Evidencia 9

Captura de:

```bash
docker ps
```

---

# 10. AMAZON ECR

# 10.1 Crear repositorio ECR

En AWS:

```plaintext
Elastic Container Registry → Create Repository
```

Nombre:

```plaintext
fastapi-aws-taller
```

---

# 10.2 Login ECR

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin TU_ID.dkr.ecr.us-east-1.amazonaws.com
```

---

# 10.3 Tag imagen

```bash
docker tag fastapi-aws-taller:latest TU_ID.dkr.ecr.us-east-1.amazonaws.com/fastapi-aws-taller:latest
```

---

# 10.4 Push imagen

```bash
docker push TU_ID.dkr.ecr.us-east-1.amazonaws.com/fastapi-aws-taller:latest
```

---

# 📸 Evidencia 10

Captura de ECR mostrando:

```plaintext
latest
```

---

# 11. AWS LAMBDA

# 11.1 Crear función

En AWS:

```plaintext
Lambda → Create Function
```

Seleccionar:

```plaintext
Container image
```

Elegir imagen de ECR.

---

# 11.2 Crear Function URL

Ir a:

```plaintext
Configuration → Function URL
```

Seleccionar:

```plaintext
Auth type → NONE
```

Crear URL.

---

# 📸 Evidencia 11

Captura mostrando:

- URL pública Lambda

---

# 12. PRUEBAS FINALES

Abrir:

```plaintext
https://URL_LAMBDA/docs
```

Probar:

## Error 415

Subir:

```plaintext
archivo .txt
```

Debe responder:

```json
{
  "detail": "Formato inválido"
}
```

---

## Subida correcta

Subir:

```plaintext
imagen PNG o JPG
```

Debe responder:

```json
{
  "mensaje": "Imagen subida correctamente"
}
```

---

# 📸 Evidencia 12

Capturas de:

- error 415
- subida exitosa

---

# 13. COMANDOS ÚTILES

## Ver contenedores

```bash
docker ps
```

## Ver logs Docker

```bash
docker logs app_taller
```

## Reiniciar servicio FastAPI

```bash
sudo systemctl restart fastapi
```

## Estado servicio

```bash
sudo systemctl status fastapi
```

## Entrar a carpeta principal

```bash
cd ~/Taller_AWS
```

---

# 14. TECNOLOGÍAS UTILIZADAS

- AWS S3
- AWS EC2
- AWS Lambda
- AWS ECR
- Python
- FastAPI
- Docker
- SQLAlchemy
- boto3
- GitHub

---

# 15. AUTOR

Proyecto desarrollado para el Taller AWS de Sistemas Operativos.
