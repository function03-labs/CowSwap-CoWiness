from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from src.compute_cow import compute_cowiness_detailed, compute_cowiness_simple

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Cowiness API",
    description="API for calculating Coincidence-of-Wants on CowSwap",
    url_scheme=True,
    default_swagger_filename="specs.json",
)
app.config.SWAGGER_UI_DOC_EXPANSION = "list"

ns = api.namespace("cowiness", description="CoW operations")


cowiness_model = api.model(
    "Cowiness",
    {
        "cowiness": fields.Float(
            description="The cowiness value for the given transaction hash",
            example="0.75",
        )
    },
)
batch_model = api.model(
    "Batch",
    {
        "cowiness": fields.Float(
            description="The cowiness value for the given batch", example=1
        ),
        "total_volume_in_usd": fields.Float(
            description="The total volume in USD of all tokens bought in the batch",
            example=291.07484530376996,
        ),
        "total_volume_out_usd": fields.Float(
            description="The total volume in USD of all tokens sold in the batch",
            example=0,
        ),
        "volume_in_usd": fields.Raw(
            description="The USD value of each token bought in the batch",
            example={
                "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
                    "amount": 0.15,
                    "usd_value": 291.07484530376996,
                    "token": {
                        "name": "Wrapped Ether",
                        "decimals": 18,
                        "priceUsd": 1940.4989686917997,
                        "amount": 0.15,
                    },
                }
            },
        ),
        "volume_out_usd": fields.Raw(
            description="The USD value of each token sold in the batch",
            example={},
        ),
        "tx_hash": fields.String(
            description="The transaction hash of the batch settlement",
            example="0xe9bb32f7ae553ebad727d2b6020b4298cb71c6f2dc96fa07f8a9ab056a93def2",
        ),
    },
)
txhash_parser = reqparse.RequestParser()
txhash_parser.add_argument(
    "batch_tx",
    type=str,
    help="Transaction hash of settlement",
    required=True,
    default="0xf87cb0b580345192314930b7059de4f873f76419bdb44feb38e1544ebe6d1c49",
)
batch_parser = reqparse.RequestParser()
batch_parser.add_argument(
    "batch_tx", type=str, help="Transaction hash of the settlement", required=True
)


@ns.route("/v1/")
class Cowiness(Resource):
    @ns.doc(
        parser=txhash_parser,
        description="Calculate the CoW of a given batch auction on CowSwap",
    )
    @ns.expect(txhash_parser)
    @ns.response(200, "Success", cowiness_model)
    @ns.response(400, "Bad Request")
    def get(self):
        """Get the CoW value for a given transaction hash of a settled batch auction"""
        args = txhash_parser.parse_args()
        txhash = args["batch_tx"]
        result = compute_cowiness_simple(txhash)
        if result:
            cowiness = result
            return {"cowiness": cowiness}
        else:
            return {"message": "Error computing CoW value"}, 500


@ns.route("/v1/extended")
class CowinessExtended(Resource):
    @ns.doc(
        parser=batch_parser,
        description="Calculate the cowiness of a given batch auction on CowSwap and return additional details",
    )
    @ns.expect(batch_parser)
    @ns.response(200, "Success", batch_model)
    @ns.response(400, "Bad Request")
    def get(self):
        """Get the cowiness value, total volume in USD, total volume out USD, and auction details of a given batch auction"""
        args = batch_parser.parse_args()
        batch_id = args["batch_tx"]
        result = compute_cowiness_detailed(batch_id)
        if result:
            return result
        else:
            return {"message": "Error computing CoW value"}, 500


if __name__ == "__main__":
    app.run(debug=True)
