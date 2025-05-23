import json
import jwt
from fastapi import FastAPI, Request, Security, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.encoders import jsonable_encoder

from config import get_config
from libs.keycloak import get_me, keycloak_init
from libs.socket import Socket


SOCKET_DISABLED = get_config('SOCKET_DISABLED', wrapper=bool)
FRONTEND_DIR = get_config('FRONTEND_DIR')


keycloak_init()
app = FastAPI(root_path='/api')

if not SOCKET_DISABLED:
    socket = Socket(app)

    @socket.event
    async def test(sid, payload):
        print(payload)


@app.get("/")
async def root():
    return FileResponse(f"{FRONTEND_DIR}/index.html")


@app.get("/me")
async def info_about_me(user=Security(get_me)):
    return user


@app.get("/config")
async def get_configuration():
    return {
        'url': get_config('KEYCLOAK_URL'),
        'clientId': get_config('KEYCLOAK_CLIENT_ID'),
        'realm': get_config('KEYCLOAK_REALM'),
    }


@app.exception_handler(jwt.ExpiredSignatureError)
async def validation_exception_handler(request: Request,
                                       exc: jwt.ExpiredSignatureError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=jsonable_encoder({
            "detail": "The JWT token expired.",
            "status": "False"
        }),
    )

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static")
