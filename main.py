"""Shim para backward compatibility. Ejecutar con: uvicorn main:app --reload"""

from app.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
