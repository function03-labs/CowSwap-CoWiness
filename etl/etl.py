import os
import requests
from schedule import every
from db.mongo import connect
from dotenv import load_dotenv

# Load .env file from the main folder
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Get environment variables
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.environ.get("MONGODB_COLLECTION_NAME")
SUBGRAPH_ENDPOINT = os.environ.get("SUBGRAPH_ENDPOINT")


# Access the desired collection
collection = connect(MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME)

# Define GraphQL query
query = """
{
  settlements(first: 10) {
    id
    txHash
    trades {
      timestamp
    }
  }
}
"""


# Define data pulling and uploading task
def etl_task():
    # Send POST request to GraphQL endpoint
    response = requests.post(SUBGRAPH_ENDPOINT, json={"query": query})

    # Extract settlement data from JSON response
    settlements = response.json()["data"]["settlements"]

    # Insert data into MongoDB
    for settlement in settlements:
        settlement["_id"] = settlement.pop("id")
        print(f"Inserted settlement {settlement['_id']}")
        collection.insert_one(settlement)


# Schedule the task to run every 5 minutes
every(5).minutes.do(etl_task)
