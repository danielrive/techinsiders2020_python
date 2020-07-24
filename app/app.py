from flask import Flask
from flask import request
from flask import make_response
import os

import boto3
from boto3.dynamodb.conditions import Attr
import botocore.exceptions

# Variables de entorno
books_table = os.environ["DYNAMODB_TABLE"]

# Inicializando servicios AWS
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(books_table)

# Inicializa Flask
app = Flask(__name__)

# Health check
@app.route("/")
def health_check():
    return {"status": "todo ok"}


@app.route("/resources/books", methods=("GET", "POST", "PUT"))
def books_resource():
    if request.method == "POST":
        try:
            data = request.form.to_dict()
            print(data)
            if data["id"] and data["name"]:
                try:
                    put_item_response = table.put_item(
                        Item=data, ConditionExpression=Attr("id").not_exists()
                    )
                    body = {
                        "message": "Book successfully created with id {}".format(
                            data["id"]
                        )
                    }
                    response = make_response(body, 201)
                    response.headers["Content-Type"] = "application/json"
                    return response

                except botocore.exceptions.ClientError:
                    body = {"error": "The specified id already exists"}
                    response = make_response(body, 400)
                    response.headers["Content-Type"] = "application/json"
                    return response

                except Exception as e:
                    print(str(e))
                    body = {"error": "There was an error creating the book"}
                    response = make_response(body, 500)
                    response.headers["Content-Type"] = "application/json"
                    return response

        except Exception as e:
            print(str(e))
            body = {"error": "You must provide a valid id and name"}
            response = make_response(body, 400)
            response.headers["Content-Type"] = "application/json"
            return response

    if request.method == "GET":
        id = request.args.get("id")
        author = request.args.get("author")
        if id:
            try:
                get_item_response = table.get_item(Key={"id": id})
                try:
                    body = {"book": get_item_response["Item"]}
                    response = make_response(body, 200)
                    response.headers["Content-Type"] = "application/json"
                    return response

                except Exception as e:
                    print(str(e))
                    body = {"error": "Book with id {} not found.".format(id)}
                    response = make_response(body, 404)
                    response.headers["Content-Type"] = "application/json"
                    return response

            except Exception as e:
                print(str(e))
                body = {"error": str(e)}
                response = make_response(body, 502)
                response.headers["Content-Type"] = "application/json"
                return response

        elif author:
            try:
                scan_response = table.scan(FilterExpression=Attr("author").eq(author))
                body = {"books": scan_response["Items"]}
                response = make_response(body, 200)
                response.headers["Content-Type"] = "application/json"
                return response

            except Exception as e:
                print(str(e))
                body = {"error": str(e)}
                response = make_response(body, 502)
                response.headers["Content-Type"] = "application/json"
                return response

        else:
            try:
                scan_response = table.scan()
                body = {"books": scan_response["Items"]}
                response = make_response(body, 200)
                response.headers["Content-Type"] = "application/json"
                return response

            except Exception as e:
                print(str(e))
                body = {"error": str(e)}
                response = make_response(body, 502)
                response.headers["Content-Type"] = "application/json"
                return response

    if request.method == "PUT":
        data = request.form.to_dict()
        try:
            if data["id"]:
                try:
                    put_item_response = table.put_item(
                        Item=data, ConditionExpression=Attr("id").exists()
                    )
                    body = {
                        "message": "Book with id {} was successfully updated".format(
                            data["id"]
                        )
                    }
                    response = make_response(body, 200)
                    response.headers["Content-Type"] = "application/json"
                    return response

                except botocore.exceptions.ClientError:
                    body = {"error": "The specified id does not exist"}
                    response = make_response(body, 404)
                    response.headers["Content-Type"] = "application/json"
                    return response

                except Exception as e:
                    print(str(e))
                    body = {
                        "error": "There was an error updating the book. Please try again"
                    }
                    response = make_response(body, 500)
                    response.headers["Content-Type"] = "application/json"
                    return response

        except Exception as e:
            print(str(e))
            body = {"error": "You must provide a valid id"}
            response = make_response(body, 400)
            response.headers["Content-Type"] = "application/json"
            return response


@app.route("/resources/books/<id>", methods=["DELETE"])
def book_id_resource(id):
    if request.method == "DELETE":
        try:
            delete_item_response = table.delete_item(
                Key={"id": id}, ConditionExpression=Attr("id").exists()
            )
            body = {"message": "Book with id {} was successfully deleted".format(id)}
            response = make_response(body, 200)
            response.headers["Content-Type"] = "application/json"
            return response

        except botocore.exceptions.ClientError:
            body = {"error": "Book with id {} not found.".format(id)}
            response = make_response(body, 404)
            response.headers["Content-Type"] = "application/json"
            return response

        except Exception as e:
            print(str(e))
            body = {"error": str(e)}
            response = make_response(body, 502)
            response.headers["Content-Type"] = "application/json"
            return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
