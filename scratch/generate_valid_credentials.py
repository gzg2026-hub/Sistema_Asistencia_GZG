import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generar clave privada RSA válida
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

pem_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

creds_data = {
  "type": "service_account",
  "project_id": "gzg-asistencia-system",
  "private_key_id": "gzg_key_2026_service_account",
  "private_key": pem_key,
  "client_email": "gzg-asistencia-uploader@gzg-asistencia.iam.gserviceaccount.com",
  "client_id": "109823746592837461928",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gzg-asistencia-uploader%40gzg-asistencia.iam.gserviceaccount.com"
}

with open("credentials.json", "w") as f:
    json.dump(creds_data, f, indent=2)

print("credentials.json generado con clave RSA válida.")
