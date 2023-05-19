# CowSwap CoWiness API and ETL

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

This repository contains two main components; an API for visualizing the Coincidence of Wants (CoW) of settled batch auctions on the Ethereum protocol CowSwap, and an ETL pipeline for ingesting batch auctions data from a Subgraph and storing it in a MongoDB database.

## Table of Contents

- [API](#api)
- [ETL](#etl)
- [Installation](#installation)
- [Usage](#usage)
- [Env Variables](#env-variables)
- [Contributing](#contributing)
- [License](#license)

## API

The API is built using Flask and Flask-RESTx, providing a RESTful interface to visualize CoW values for settled batch auctions on CowSwap.

### Endpoints

- `/cowiness/v1/`: Get the CoW value for a given transaction hash of a settled batch auction.
- `/cowiness/v1/extended`: Get the CoW value, total volume in USD, total volume out USD, and auction details of a given batch auction.

## ETL

The ETL pipeline pulls data from the CowSwap Subgraph, processes it, and stores it in a MongoDB database. The pipeline is scheduled to run every 5 minutes, ensuring that the database is continually up-to-date.

## Installation

1. Clone the repository:

```
git clone https://github.com/0xaaiden/cowswap-cowiness.git
```

2. Change to the repository directory:

```
cd cowswap-cowiness
```

3. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Start the API:

```
python api/app.py
```

2. Start the ETL pipeline:

```
python etl/main.py
```

3. Access the API endpoints in your browser or using a tool like Postman:

- `http://localhost:5000/cowiness/v1/?batch_tx=<transaction_hash>`
- `http://localhost:5000/cowiness/v1/extended?batch_tx=<transaction_hash>`

Replace `<transaction_hash>` with the desired transaction hash.

### Swagger UI

You can access the Swagger UI for the API at `http://localhost:5000/docs`. This provides a convenient way to explore the API endpoints and test them interactively.

## Env Variables

Create a `.env` file and add the following environment variables:

```
#Only needed to run the ETL service
MONGODB_URI=<your_mongodb_uri>
MONGODB_DB_NAME=<your_mongodb_database_name>
MONGODB_COLLECTION_NAME=<your_mongodb_collection_name>
START_TIMESTAMP=UNIX_TIMESTAMP

#Required to run the API
SUBGRAPH_ENDPOINT=<your_subgraph_endpoint>
ORDERBOOK_URL=https://api.cow.fi/mainnet
WEB3_URL=<eth_node_rpc_url>

```

Replace the placeholder values with the actual values for your MongoDB instance and Subgraph endpoint.

For example:

```
MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net
MONGODB_DB_NAME=cow_batches
MONGODB_COLLECTION_NAME=last_batches
SUBGRAPH_ENDPOINT=https://api.thegraph.com/subgraphs/name/cowprotocol/cow
ORDERBOOK_URL=https://api.cow.fi/mainnet
WEB3_URL=https://eth.llamarpc.com
START_TIMESTAMP=UNIX_TIMESTAMP
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the [MIT](https://choosealicense.com/licenses/mit/) file for details.
