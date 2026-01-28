import json
from app.core.db import get_table, init_db
from app.core.config import settings
from app.core.logging import logger

def ingest_data():
    """Ingests initial data from JSON to DynamoDB."""
    # Ensure table exists
    init_db()
    
    table = get_table()
    
    try:
        with open("scoopsxi-dataset-20250123.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        logger.info(f"Ingesting {len(data)} records into DynamoDB...")
        
        with table.batch_writer() as batch:
            for item in data:
                batch.put_item(Item={
                    "id": str(item["id"]),
                    "date": item["date"],
                    "nps": int(item["nps"]),
                    "csat": int(item["csat"]),
                    "ces": int(item["ces"]),
                    "comment": item["comment"]
                })
        
        logger.info("Ingestion complete.")
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")

if __name__ == "__main__":
    ingest_data()
