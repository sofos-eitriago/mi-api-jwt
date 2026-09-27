from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_token, get_current_user, hash_password, verify_password

app = FastAPI(title="API con JWT", description="LPR07304 · Semana 10 · Autenticación JWT en FastAPI")

# Base de datos simulada (en producción: PostgreSQL). Contraseñas guardadas como hash bcrypt.
fake_users = {
    "maria@ujap.edu.ve": {"hashed": hash_password("profe123"), "role": "profesor"},
    "estudiante@ujap.edu.ve": {"hashed": hash_password("estu123"), "role": "estudiante"},
}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = fake_users.get(form.username)
    if not user or not verify_password(form.password, user["hashed"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token({"sub": form.username, "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/publico")
def ruta_publica():
    return {"msg": "Cualquiera puede ver esto"}


@app.get("/privado")
def ruta_privada(user: dict = Depends(get_current_user)):
    return {"msg": f"Hola {user['sub']}, rol: {user['role']}"}


@app.get("/admin")
def ruta_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo para profesores")
    return {"msg": "Panel de administración"}
