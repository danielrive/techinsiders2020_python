from flask import Flask
from flask import request
import os

import boto3
from boto3.dynamodb.conditions.Attr import ConditionExpression

# Variables de entorno
books_table = os.environ["DYNAMODB_TABLE"]

# Inicializando servicios AWS
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(books_table)

# Inicializando variables Globales
response = {
    'statusCode': 502,
    'body': '',
    'headers': ''
}

# Inicializa Flask
app = Flask(__name__)
@app.route('/')

# Health check
def health_check():
    return {'status': 'Ok'}


@app.route('/resources/books', methods=('GET', 'POST', 'PUT'))
def books_resource():
    if request.method == 'POST':
        data = request.form
        try:
            put_item_response = table.put_item(
                Item=data
                ConditionExpression=Attr('id').not_exists()
            )
            print(put_item_response)
        except Exception as e:
            print(e)

    if request.method == 'GET':
        id = request.args.get('id')
        author = request.args.get('author')
        year = request.args.get('year')
        topic = request.args.get('topic')
        if id:
            try:
                response["body"] = get_element(id)
                response["statusCode"] = 200
            except Exception as e:
                print(str(e))

        else:
            try:
                scan_response = table.scan(
                    IndexName='id',
                    FilterExpression=Attr('author').eq(author)
                )
                print(scan_response)
            except Exception as e:
                print(str(e))

    if request.method == 'PUT':
        data = request.form
        try:
            item_id = get_element(id)["id"]
            data["id"] = item_id
            put_item_response = table.put_item(
                Item=data
            )
            print(put_item_response)
        except Exception as e:
            print(e)

@app.route('/resources/books/<id>', methods=['DELETE'])
def book_id_resource(id):
    if request.method == 'DELETE':
        id = request.args.get('id')
        try:
            delete_item_response = table.delete_item(
                Key={
                    'id': id
                }
            )
            response["body"] = delete_item_response["Attributes"]
            response["statusCode"] = 200

            return response

        except Exception as e:
            print(str(e))

def get_element(id):
    get_item_response = table.get_item(
        Key={
            'id': id
        }
    )
    return get_item_response["Item"]



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
