import os
from dotenv import load_dotenv
from pyiceberg.catalog import load_catalog
from typing import Dict, List

load_dotenv()

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

def add_files_to_tables(table_file_map: Dict[str, List[str]]):
    catalog = get_catalog()

    for table_name, file_paths in table_file_map.items():
        table = catalog.load_table(table_name)
        table.add_files(file_paths)
        print(f"✅ Files added and snapshot committed for table: {table_name}")
