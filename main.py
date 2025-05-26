from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import uvicorn
from utils import add_files_to_tables

app = FastAPI()

class FilePayload(BaseModel):
    table_name: str
    file_path: str

@app.post("/add_files")
async def add_files(payload: List[FilePayload]):
    table_map = {}
    for item in payload:
        if item.table_name in table_map:
            table_map[item.table_name].append(item.file_path)
        else:
            table_map[item.table_name] = [item.file_path]

    try:
        add_files_to_tables(table_map)
        return {"status": "success", "message": "Files added to tables."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)