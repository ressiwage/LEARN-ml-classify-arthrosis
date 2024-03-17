from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from json import JSONDecodeError
import aiofiles
import os, json
import numpy as np
import utils
import debug, model, preprocess
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from fastapi import File, UploadFile

# debug: bool = 0, features: bool=0, brightness: int = 1
def checker(data: str = Form(...)):
    try:
       return json.loads(data)
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid JSON data')

@app.post("/predict")
def predict(file: UploadFile, debug: bool = 0, features: bool=0, brightness: int = 1 ):
    print(file)
    result = {}
    try:
        contents = file.file.read()
        with open(file.filename, "wb+") as f:
            f.write(contents)
        result = utils.predict(file.filename, debug, features, brightness)
    except Exception as e:
        raise e
        return {"message": f"There was an error uploading the file: {e}"}
    finally:
        file.file.close()

    return json.dumps({
        "payload":result.get("prediction", "error"),
        "filenames":result.get("debug_imgs", "")
    }, ensure_ascii=False, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x) 



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello, World!"})
