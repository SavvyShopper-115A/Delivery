from datetime import datetime
from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow import Schema, ValidationError, fields, validates

app = Flask(__name__)
ma = Marshmallow(app)


class RetailerSchema(Schema):
    name = fields.String(required=True)
    icon = fields.URL(required=True)

class ItemSchema(Schema):
    url = fields.URL(required=True)
    nickname = fields.String(required=True)
    uid = fields.String(required=True)
    retailer = fields.Nested(RetailerSchema, required=True)
    price_data = fields.List(fields.Float(), required=True)
    status = fields.String(required=True)
    desired_price = fields.Float(required=True)
    start_date = fields.String(required=True)
    item_name = fields.String(required=True)
    @validates("start_date")
    def validate_start_date(self, start_date):
        try:
            datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError as e:
            print(e)
            raise ValidationError("Invalid start date format. Must be a valid ISO string.")
        
class NewItemSchema(Schema):
    itemId = fields.String(required=True)

class NameAndPriceSchema(Schema):
    name = fields.String(required=True)
    price = fields.Float()

def validate_name_and_price_data(data):
    try:
        schema = NameAndPriceSchema()
        item_data = schema.load(data)
        return item_data
    except ValidationError as e:
        print(e)
        return False

def validate_new_item_data(data):
    try:
        schema = NewItemSchema()
        item_data = schema.load(data)
        return item_data
    except ValidationError as e:
        print(e)
        return False

def validate_item_data(data):
    try:
        schema = ItemSchema()
        item_data = schema.load(data)
        return item_data
    except ValidationError as e:
        print(e)
        return False