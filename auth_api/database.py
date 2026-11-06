"""Conexión a MySQL con SQLAlchemy, opcionalmente a través de un túnel SSH.

Si SSH_HOST está definido, se abre un túnel:
    puerto local libre (127.0.0.1:XXXXX)  ──SSH──►  servidor SSH  ──►  DB_HOST:DB_PORT
y SQLAlchemy se conecta al extremo local del túnel. Es lo mismo que hace DBeaver con
"Use SSH Tunnel".
"""
import atexit
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

# Host y puerto de MySQL VISTOS DESDE el servidor SSH (si MySQL corre en la misma
# máquina EC2, es 127.0.0.1:3306; si es un RDS, el endpoint del RDS).
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = int(os.getenv("DB_PORT", "3306"))

if os.getenv("SSH_HOST"):
    from sshtunnel import SSHTunnelForwarder

    key_path = os.environ["SSH_PRIVATE_KEY"]
    if key_path.lower().endswith(".ppk"):
        raise RuntimeError(
            "La llave .ppk (formato PuTTY) no es compatible con paramiko. Conviértela a OpenSSH:\n"
            f'  puttygen "{key_path}" -O private-openssh -o "{key_path[:-4]}.pem"\n'
            "y apunta SSH_PRIVATE_KEY al archivo .pem"
        )

    tunnel = SSHTunnelForwarder(
        (os.environ["SSH_HOST"], int(os.getenv("SSH_PORT", "22"))),
        ssh_username=os.environ["SSH_USER"],
        ssh_pkey=key_path,
        ssh_private_key_password=os.getenv("SSH_KEY_PASSPHRASE") or None,
        remote_bind_address=(db_host, db_port),
        local_bind_address=("127.0.0.1", 0),  # 0 = el sistema elige un puerto local libre
        allow_agent=False,                    # usar solo la llave indicada
        host_pkey_directories=[],
        set_keepalive=30,                     # evita que el túnel se cierre por inactividad
    )
    tunnel.start()
    atexit.register(tunnel.stop)
    db_host, db_port = "127.0.0.1", tunnel.local_bind_port

# URL.create escapa correctamente claves con caracteres especiales (@, :, /, #...)
url = URL.create(
    "mysql+pymysql",
    username=os.environ["DB_USER"],
    password=os.getenv("DB_PASSWORD", ""),
    host=db_host,
    port=db_port,
    database=os.environ["DB_NAME"],
    query={"charset": "utf8mb4"},
)

engine = create_engine(url, pool_pre_ping=True, pool_recycle=280)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
