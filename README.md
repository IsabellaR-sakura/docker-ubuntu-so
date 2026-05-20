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
--bucket user-20052026-ueia-so \
--region us-east-2
```


---

# 📸 Evidencia

<img width="1329" height="405" alt="image" src="https://github.com/user-attachments/assets/8c8f1d91-ae20-4883-a2a1-adb6e5174adc" />


---

# 2.2 Crear archivo local

Seguimos en:

```plaintext
~/Taller_AWS
```

Crear archivo:

```bash
echo "macarena" > archivoprue.txt
```

Verificar:

```bash
ls
```

---

# 2.3 Subir archivo a S3 usando AWS CLI

```bash
aws s3 cp archivoprue.txt s3://user-20052026-ueia-so/archivoprue.txt
```

---

# 2.4 Verificar contenido del bucket

```bash
aws s3 ls s3://user-20052026-ueia-so/
```

---

# 📸 Evidencia

<img width="2536" height="155" alt="Captura de pantalla 2026-05-20 111515" src="https://github.com/user-attachments/assets/28c87986-8ba6-48d9-82e6-04fc0a847941" />

---

# 2.5 Descargar archivo desde S3

Crear carpeta:

```bash
mkdir descargas
```

Descargar:

```bash
aws s3 cp \
s3://user-20052026-ueia-so/archivoprue.txt \
./descargas/archivoprue.txt
```

Entrar a la carpeta:

```bash
cd descargas
```

Verificar:

```bash
ls -l
```

---

# 📸 Evidencia 

<img width="2559" height="97" alt="image" src="https://github.com/user-attachments/assets/3b802e22-3020-4b03-9c98-7ffb5b995945" />

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
BUCKET_NAME = 'user-20052026-ueia-so'

# 1. Cargar archivo individual
s3.upload_file('archivoprue.txt', BUCKET_NAME, 'boto3_archivoprue.txt')
print("[OK] Archivo individual cargado con boto3.")

# 2. Descargar en otra carpeta diferente
os.makedirs('descargas_boto3', exist_ok=True)
s3.download_file(BUCKET_NAME, 'boto3_archivoprue.txt', 'descargas_boto3/boto3_archivoprue.txt')
print("[OK] Archivo individual descargado con boto3.")

# 3. Prueba con 3 archivos de texto (Múltiples archivos)
archivos = ['test1.txt', 'test2.txt', 'test3.txt']
for a in archivos:
    with open(a, 'w') as f:
        f.write(f"Contenido temporal de {a}")

# Carga múltiple iterativa
for a in archivos:
    s3.upload_file(a, BUCKET_NAME, f"multi/{a}")
print("[OK] Tres archivos de texto cargados en la carpeta 'multi/'.")

# Descarga múltiple iterativa
for a in archivos:
    s3.download_file(BUCKET_NAME, f"multi/{a}", f"descargas_boto3/{a}")
print("[OK] Tres archivos de texto descargados localmente.")
```

# 3.3 Ejecutar script

```bash
python3 s3_test.py
```

---

# 📸 Evidencia

<img width="921" height="46" alt="image" src="https://github.com/user-attachments/assets/1a750171-8a27-4323-91a1-6db5742151e4" />

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

---

# 4.4 Crear Dockerfile

```bash
nano Dockerfile
```

Pegar:

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["main.handler"]
```

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

# 📸 Evidencia 

<img width="921" height="506" alt="image" src="https://github.com/user-attachments/assets/1a57a63d-04b0-44e7-a299-cbe9f87a2aeb" />

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
Servidor-Fastapi-So
```

## Sistema operativo

```plaintext
Ubuntu 22.04 LTS
```

## Tipo

```plaintext
t3.micro
```

## Key Pair

Crear:

```plaintext
key-taller.pem
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

# 📸 Evidencia 

<img width="921" height="484" alt="image" src="https://github.com/user-attachments/assets/70290893-ffa7-4d1a-8594-9a4b1789a3b9" />

---

# 6.3 Conectarse por SSH

Desde:

```plaintext
~/Taller_AWS
```

Ejecutar:

```bash
chmod 400 key-taller.pem
```

Conectarse:

```bash
ssh -i "key-taller.pem" ubuntu@IP_PUBLICA
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

# 📸 Evidencia 

<img width="926" height="92" alt="image" src="https://github.com/user-attachments/assets/d2e277f8-e432-4450-8c0c-5d4a52a345f9" />

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

# 📸 Evidencia 

<img width="918" height="182" alt="image" src="https://github.com/user-attachments/assets/e5a4d648-5a8b-43bf-acfa-87f8abe08aa4" />

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

<img width="921" height="411" alt="image" src="https://github.com/user-attachments/assets/b945fd25-01c9-4cf2-832a-2cedba8bd677" />

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
DOCKER_BUILDKIT=0 docker build --platform linux/amd64 -t fastapi-aws-taller .
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

# 📸 Evidencia

<img width="921" height="171" alt="image" src="https://github.com/user-attachments/assets/23bf6dd1-2d27-4c06-9365-1b14e8449ad1" />

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

# 📸 Evidencia

<img width="921" height="504" alt="image" src="https://github.com/user-attachments/assets/e84ef59a-f522-4c13-8e93-b765f117c6fe" />

---


# 15. AUTOR

Isabella Ramirez Tobon - Valentina Santana Moncada
