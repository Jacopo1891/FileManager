from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import shutil, uvicorn
from datetime import datetime

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_unique_filename(filename):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        return filename
    
    name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
    counter = 1
    while (UPLOAD_DIR / f"{name}({counter}).{ext}").exists():
        counter += 1
    return f"{name}({counter}).{ext}" if ext else f"{name}({counter})"

def get_file_list():
    return [
        {"name": f.name, "uploadDate": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
        for f in UPLOAD_DIR.iterdir() if f.is_file()
    ]

@app.get("/files/")
async def list_files():
    return {"files": get_file_list()}

@app.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    for file in files:
        unique_filename = get_unique_filename(file.filename)
        file_path = UPLOAD_DIR / unique_filename
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file.file.close()  # Rilascia il file una volta caricato
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Errore nel salvataggio di {file.filename}: {str(e)}"})
    return {"message": "File caricati con successo"}

@app.delete("/delete/{filename}")
async def delete_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return {"message": f"{filename} eliminato con successo"}
    return JSONResponse(status_code=404, content={"message": "File non trovato"})

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, filename=filename)
    return JSONResponse(status_code=404, content={"message": "File non trovato"})

@app.put("/rename/{old_name}")
async def rename_file(old_name: str, data: dict):
    new_name = data.get("new_name")
    old_path = UPLOAD_DIR / old_name
    new_path = UPLOAD_DIR / new_name

    if not old_path.exists():
        raise HTTPException(status_code=404, detail="File non trovato")
    
    if new_path.exists():
        raise HTTPException(status_code=400, detail="Esiste già un file con questo nome")
    
    old_path.rename(new_path)
    return {"message": f"{old_name} rinominato in {new_name}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234)