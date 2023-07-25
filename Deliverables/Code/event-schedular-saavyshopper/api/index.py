from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime
import os
from dotenv import load_dotenv
import re
import json
from api.middleware import user_authentication
from api.schema import validate_item_data, validate_new_item_data, validate_name_and_price_data
from api.auth_server import db
from firebase_admin import auth
import redis

retailer_dict = {
    "bestbuy": {
        "name": "Best Buy",
        "icon": "https://gist.githubusercontent.com/Ankur-0429/320fcd0fbfdcd851662040ff2155743d/raw/756be7159f1d4a9a19a07a17c54aafb007a8ade4/bestbuy.svg"
    },
    "ebay": {
        "name": "Ebay",
        "icon": "https://upload.wikimedia.org/wikipedia/commons/1/1b/EBay_logo.svg"
    },
    "newegg": {
        "name": "Newegg",
        "icon": "https://gist.githubusercontent.com/Ankur-0429/edbf589fe7fe8efa1658c73fe5ef9829/raw/06e10c71957d09efa13093210479e375bbdf2ddc/newegg.svg"
    },
    "amazon": {
        "name": "Amazon",
        "icon": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
    },
    "craigslist": {
        "name": "Craigslist",
        "icon": "https://upload.wikimedia.org/wikipedia/commons/c/c6/Craigslist.svg"
    },
    "walmart": {
        "name": "Walmart",
        "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Walmart_Spark.svg/963px-Walmart_Spark.svg.png"
    }
}

r = redis.Redis(
  host='fitting-crab-43054.upstash.io',
  port=43054,
  password=os.getenv("REDIS_PASS"),
  ssl=True
)


RETAILER_PATTERNS = {
    "bestbuy": r"^(https?://)?(www\.)?bestbuy\.com",
    "ebay": r"^(https?://)?(www\.)?ebay\.com",
    "newegg": r"^(https?://)?(www\.)?newegg\.com",
    "amazon": r"^(https?://)?(www\.)?amazon\.com",
    "craigslist": r"(https?://)?([a-zA-Z0-9]+\.)?craigslist\.org",
    "walmart": r"^(https?://)?(www\.)?walmart\.com",
}

def check_retailer(url):
    for retailer, pattern in RETAILER_PATTERNS.items():
        if re.match(pattern, url):
            return retailer
    return None


load_dotenv()
app = Flask(__name__)
CORS(app)

@app.route('/sendWelcomeEmailToUser', methods=['GET'])
@user_authentication()
def sendWelcomeEmailToUser(user_token):
    try:
        email = user_token['email']
        url = f"{os.getenv('EMAIL_API_URL')}/sendWelcomeEmailToUser?email={email}"
        response = requests.get(url)

        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/deleteTask', methods=['POST'])
@user_authentication()
def deleteTask(user_token):
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return jsonify({"error": "Content-Type not supported!"}), 400
    
    jsonData = request.json
    itemIdData = validate_new_item_data(jsonData)
    if (itemIdData == False):
        return jsonify({"error": "item id is not formatted correctly"}), 400
    
    doc_ref = db.collection("items").document(itemIdData['itemId'])
    doc_snapshot = doc_ref.get()

    if not doc_snapshot.exists:
        return jsonify({"error": "item does not exist"}), 400
    
    document_data = doc_snapshot.to_dict()

    if (document_data['uid'] != user_token['uid']):
        return jsonify({"error": "you don't have access to this task"})
    
    doc_ref.delete()

    return jsonify({"success": "item deleted"})

@app.route('/editTask', methods=['POST'])
@user_authentication()
def editTask(user_token):
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return jsonify({"error": "Content-Type not supported!"}), 400
    jsonData = request.json
    jsonData['uid'] = user_token['uid']
    jsonData['status'] = 'processing'
    
    if ('id' not in jsonData):
        return jsonify({'error': 'id not found'}), 400
    id = jsonData.pop('id')

    data = validate_item_data(jsonData)
    if (data == False):
        return jsonify({"error": "item data is not formatted correctly"}), 400
    
    
    doc_ref = db.collection("items").document(id)
    doc_snapshot = doc_ref.get()

    if not doc_snapshot.exists:
        return jsonify({"error": "item does not exist"}), 400
    
    document_data = doc_snapshot.to_dict()

    if (document_data['uid'] != data['uid']):
        return jsonify({"error": "you don't have access to this task"})
    
    doc_ref.update(data)

    return jsonify({"success": "data has been edited"}), 200


@app.route('/schedule', methods=['POST'])
@user_authentication()
def schedule(user_token):
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return jsonify({"error": "Content-Type not supported!"}), 400

    jsonData = request.json
    jsonData['uid'] = user_token['uid']
    jsonData['status'] = 'processing'
    data = validate_item_data(jsonData)
    if (data == False):
        return jsonify({"error": "item data is not formatted correctly"}), 400
    
    collection_ref = db.collection("items")
    query = collection_ref.where('uid', '==', data['uid']).where('url', '==', data['url'])

    docs = query.get()

    if (len(docs) > 0):
        return jsonify({"error": "user is already tracking this item"}), 400

    doc_ref = db.collection("items").document()
    doc_ref.set(data)

    body = {
        "itemId": doc_ref.id
    }

    stringify_body = json.dumps(body)

    url = "https://api.cron-job.org/jobs"

    payload = {
        "job": {
            "url": "https://event-schedular-saavyshopper.vercel.app/addNewPriceData",
            "requestMethod": 1,
            "enabled": "true",
            "saveResponses": True,
            "schedule": {
                "timezone": "America/Los_Angeles",
                "expiresAt": (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y%m%d%H%M%S"),
                "hours": [0],
                "mdays": [-1],
                "minutes": [0],
                "months": [-1],
                "wdays": [-1] 
            },
            "extendedData": {
                "body": stringify_body,
                "headers": {
                    'Content-Type': 'application/json'
                }
            }
        }
    }

    headers = {
        'Authorization': "Bearer " + os.getenv('CRON_JOB_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.put(url, data=json.dumps(payload), headers=headers, json=stringify_body)

    return jsonify({"success": response.status_code}), 201

def get_user_email_from_uid(uid):
    try:
        user = auth.get_user(uid)
        return user.email
    except auth.UserNotFoundError:
        return None

@app.route('/addNewPriceData', methods=['POST'])
def addNewPriceData():
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return jsonify({"error": "Content-Type not supported!"}), 400

    jsonData = request.json
    itemIdData = validate_new_item_data(jsonData)
    if (itemIdData == False):
        return jsonify({"error": "item id is not formatted correctly"}), 400
    
    doc_ref = db.collection("items").document(itemIdData['itemId'])
    doc_snapshot = doc_ref.get()

    if not doc_snapshot.exists:
        return jsonify({"error": "item does not exist"}), 400

    document_data = doc_snapshot.to_dict()

    data = validate_item_data(document_data)
    uid = data['uid']
    item_name = data['item_name']
    if (data == False):
        doc_ref.update({
            'status': 'stopped'
        })
        return jsonify({"error": "item data is not formatted correctly"}), 400
    
    if data["status"] != "processing":
        return jsonify({"error": "data has already ended"}), 400
    
    retailer = check_retailer(data["url"])
    if (retailer is None):
        response = {
            'error': 'current retailer not supported',
            'message': 'The given url has a retailer that is not supported by our service'
        }
        doc_ref.update({
            'status': 'stopped'
        })
        return jsonify(response), 400
    
    url = f"{os.getenv('API_URL')}/{retailer}?url={data['url']}"
    response = requests.get(url)
    data = json.loads(response.text)

    data = validate_name_and_price_data(data)
    if (data == False):
        doc_ref.update({
            'status': 'stopped'
        })
        return jsonify({"error": "data not found"}), 400
    
    price_data = document_data.get("price_data", [])

    # Append the new price to the array
    price_data.append(data["price"])

    # Update the price_data field with the modified array
    doc_ref.update({"price_data": price_data})

    if (data["price"] <= document_data["desired_price"]):
        doc_ref.update({
            'status': 'completed'
        })
        newUrl = f"https://email-service-savvyshopper.vercel.app/priceReached?name={item_name}&itemId={itemIdData['itemId']}&email={get_user_email_from_uid(uid)}"
        response = requests.get(newUrl)

    data['retailer'] = retailer

    r.set(url, json.dumps(data))

    return jsonify(data), 200

@app.route('/findAllItemsOfUser', methods=['GET'])
@user_authentication()
def findAllItemsOfUser(user_token):
    uid = user_token['uid']
    collection_name = 'items'

    docs = db.collection(collection_name).where('uid', '==', uid).get()

    data = []

    for doc in docs:
        doc_data = doc.to_dict()
        
        # if we checked for longer than 30 days and still nothing
        # we stop it
        if (len(doc_data['price_data']) > 30):
            doc_ref = db.collection(collection_name).document(doc.id)
            doc_ref.update({
                'status': 'stopped'
            })
            doc_data['status'] = 'stopped'

        doc_data['id'] = doc.id
        data.append(doc_data)
    
    return jsonify(data), 200

@app.route('/findSingleItemOfUser', methods=['GET'])
@user_authentication()
def findSingleItemOfUser(user_token):
    uid = user_token['uid']
    
    item_id = request.args.get('itemid')
    if item_id is None:
        return jsonify({"error": "itemid parameter is missing"}), 400
    
    doc_ref = db.collection("items").document(item_id)
    doc_snapshot = doc_ref.get()

    if not doc_snapshot.exists:
        return jsonify({"error": "item does not exist"}), 400
    
    document_data = doc_snapshot.to_dict()

    if (document_data['uid'] != uid):
        return jsonify({'error': 'incorrect user'}), 400
    
    data = validate_item_data(document_data)
    if (data == False):
        doc_ref.update({
            'status': 'stopped'
        })
        return jsonify({"error": "item data is not formatted correctly"}), 400
    
    return jsonify(document_data), 200
        


@app.route('/search', methods=['GET'])
def search():
    url = request.args.get('url')
    if (url is None):
        response = {
            'error': 'Missing url query parameter',
            'message': 'The parameter is required in the URL query.'
        }
        return jsonify(response), 400
    
    retrieved_value = r.get(url)
    if retrieved_value is not None:
        return retrieved_value.decode(), 200

    valid_url = r"^(http(s):\/\/.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$"
    if (re.match(valid_url, url) is None):
        response = {
            'error': 'invalid url',
            'message': 'The given url parameter is invalid'
        }
        return jsonify(response), 400

    retailer = check_retailer(url)
    if (retailer is None):
        response = {
            'error': 'current retailer not supported',
            'message': 'The given url has a retailer that is not supported by our service'
        }
        return jsonify(response), 400

    newUrl = f"{os.getenv('API_URL')}/{retailer}?url={url}"
    response = requests.get(newUrl)

    data = json.loads(response.text)
    data = validate_name_and_price_data(data)
    if (data == False):
        return jsonify({"error": "unexpected error on our end"}), 500

    data["retailer"] = retailer_dict[retailer]

    r.set(url, json.dumps(data))

    return jsonify(data), 200


if __name__ == '__main__':
    app.run()
