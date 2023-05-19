import os
import requests
import time
import coloredlogs
import logging
from schedule import every
from db.mongo import connect
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError
import sys
from src.compute_cow import compute_cowiness_simple

# Load .env file from the main folder
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Get environment variables
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.environ.get("MONGODB_COLLECTION_NAME")
SUBGRAPH_ENDPOINT = os.environ.get("SUBGRAPH_ENDPOINT")
STARTTIMESTAMP = os.environ.get("START_TIMESTAMP")  # New environment variable
# Access the desired collection
collection = connect(MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO, logger=logger)
# Define GraphQL query with firstTradeTimestamp and limit parameters
query = """
query Settlements($timestamp: Int!, $limit: Int!) {
  settlements(
    where: { firstTradeTimestamp_gt: $timestamp }
    first: $limit
    orderBy: firstTradeTimestamp
    orderDirection: asc
  ) {
   
        firstTradeTimestamp
        id
        txHash
        solver {
          address
          id
        }
        trades {
          buyAmount
          buyAmountEth
          buyAmountUsd
          buyToken {
            address
            id
            name
            priceUsd
            priceEth
            symbol
          }
          feeAmount
          id
          sellAmountEth
          sellAmountUsd
          sellAmount
          sellToken {
            address
            id
            name
            priceEth
            priceUsd
            symbol
          }
          timestamp
       
    }
  }
}
"""
# Check if there is a saved last firstTradeTimestamp
try:
    with open("last_timestamp.txt", "r") as f:
        print(f)
        last_timestamps = f.readlines()
        if last_timestamps:
            STARTTIMESTAMP = last_timestamps[-1].strip()
except:
    pass


# Define data pulling and uploading task
def etl_task():
    global STARTTIMESTAMP
    # Send POST request to GraphQL endpoint with variables
    print("Starts: ", STARTTIMESTAMP)

    logger.info(f"Starting import from Subgraph with START_TIMESTAMP {STARTTIMESTAMP}")
    response = requests.post(
        SUBGRAPH_ENDPOINT,
        json={
            "query": query,
            "variables": {"timestamp": int(STARTTIMESTAMP), "limit": 50},
        },
    )

    # Extract settlement data from JSON response
    # print(response.json())
    settlements = response.json()["data"]["settlements"]

    # Check if settlements is not empty
    if settlements:
        # Insert data into MongoDB
        for settlement in settlements:
            settlement = settlement
            settlement["_id"] = settlement.pop("id")

            # Compute cowiness
            tx_hash = settlement["txHash"]
            result = compute_cowiness_simple(tx_hash)

            # Add cowiness to settlement
            settlement["cowiness"] = result

            try:
                collection.insert_one(settlement)
                logger.info(f"Inserted settlement {settlement['_id']}, cow: {result}")
            except DuplicateKeyError as e:
                logger.error(f"Skipping duplicate settlement {settlement['_id']}: {e}")

        # Update START_TIMESTAMP with the last firstTradeTimestamp
        last_timestamp = settlements[-1]["firstTradeTimestamp"]
        STARTTIMESTAMP = last_timestamp

        # Save the last firstTradeTimestamp
        with open("last_timestamp.txt", "a") as f:
            f.write(str(last_timestamp) + "\n")
        logger.info(
            f"Finished import from Subgraph with START_TIMESTAMP {STARTTIMESTAMP}"
        )
    else:
        logger.info("No new settlements found")


# Run the task once immediately
etl_task()

# Schedule the task to run every 5 minutes
every(5).seconds.do(etl_task)
