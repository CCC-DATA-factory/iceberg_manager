import os
from dotenv import load_dotenv
from pyiceberg.catalog import load_catalog
from typing import Dict, List
import pyarrow.parquet as pq
import pyarrow.compute as pc
import pyarrow as pa
import s3fs

load_dotenv()

fs = s3fs.S3FileSystem(
    key=os.getenv("S3_ACCESS_KEY"),
    secret=os.getenv("S3_SECRET_KEY"),
    client_kwargs={
        "endpoint_url": os.getenv("S3_ENDPOINT"),
    }
)

def read_parquet_from_s3(s3_path: str):
    with fs.open(s3_path, "rb") as f:
        table = pq.read_table(f)
        print(table.schema)
    return table

def convert_timestamps_precision(table, target_unit='us'):
    
    for field in table.schema:
        if pa.types.is_timestamp(field.type):
            # Cast timestamps to the desired precision (unit)
            if field.type.unit != target_unit:
                new_type = pa.timestamp(target_unit)
                col = pc.cast(table[field.name], new_type)
                table = table.set_column(table.schema.get_field_index(field.name), field.name, col)
    return table

def get_catalog():
    conf = {
        "type": "rest",
        "uri": os.getenv("CATALOG_URI"),
        "warehouse": os.getenv("WAREHOUSE"),
        "s3.access-key-id": os.getenv("S3_ACCESS_KEY"),
        "s3.secret-access-key": os.getenv("S3_SECRET_KEY"),
        "s3.endpoint": os.getenv("S3_ENDPOINT"),
        "s3.path-style-access": True,
        "s3.region": os.getenv("S3_REGION"),
        "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        "py-io-impl-args": {
            "pyarrow.filesystem": "pyiceberg.io.pyarrow.MinioFileSystem",
            "pyarrow.filesystem-args": {
                "endpoint": os.getenv("S3_ENDPOINT"),
                "access-key-id": os.getenv("S3_ACCESS_KEY"),
                "secret-access-key": os.getenv("S3_SECRET_KEY"),
                "path-style-access": True,
                "use-ssl": False
            }
        }
    }
    return load_catalog("minio_catalog", **conf)

def add_data_to_tables(table_name,file_path):
    catalog = get_catalog()
    table = catalog.load_table(table_name)
    data = read_parquet_from_s3(file_path)
    corrected_data = convert_timestamps_precision(data)
    table.append(corrected_data)
    print(f"✅ data is added and committed for table: {table_name}")
