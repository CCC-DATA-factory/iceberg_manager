from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import uvicorn
from utils import add_data_to_tables

app = FastAPI()

class FilePayload(BaseModel):
    table_name: str
    file_path: str

@app.post(
    "/add_data",
    responses={
        200: {
            "description": "Files successfully added to Iceberg tables."
        },
        422: {
            "description": "Validation Error. The payload structure is incorrect."
        },
        500: {
            "description": "Internal Server Error. Failed to process or insert files.",
            "content": {
                "application/json": {
                    "example": {"detail": "Error message here"}
                }
            }
        },
    }
)
async def add_files(payload: FilePayload):
    try:
        add_data_to_tables(payload.table_name,payload.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
