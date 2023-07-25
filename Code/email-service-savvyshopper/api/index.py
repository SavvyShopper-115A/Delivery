from flask import Flask, jsonify, request
from flask_cors import CORS
import smtplib
import ssl
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

#Email Params 
sender_email = "savvyshopperbot@gmail.com"
password = "nvvc ltwi eoly sapp"

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/sendWelcomeEmailToUser', methods=['GET'])
def sendWelcomeEmailToUser():
    try:
        with open("api/test.html", "r") as file:
            html_body = file.read()

        email = request.args.get('email')
        if (email is None):
            response = {
                'error': 'Missing email query parameter',
                'message': 'The parameter is required in the URL query.'
            }
            return jsonify(response), 400

        #Formatting 
        em = EmailMessage()
        em['From'] = sender_email
        em['To'] = email
        em['Subject'] = "Welcome to SavvyShopper"
        em.set_content(html_body, subtype='html')

        #extra security 
        ssl.create_default_context()

        #sends Email 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, em.as_string())
        server.quit() 

        return jsonify({"success": True, "message": "Welcome email sent successfully"}), 200

    except FileNotFoundError:
        return jsonify({"success": False, "message": "Template file not found"}), 404
    except smtplib.SMTPException as e:
        return jsonify({"success": False, "message": f"Failed to send email: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@app.route('/priceReached', methods=['GET'])
def priceReacted():
    try:
        with open("api/test2.html", "r") as file:
            html_body = file.read()

        email = request.args.get('email')
        if (email is None):
            response = {
                'error': 'Missing email query parameter',
                'message': 'The parameter is required in the URL query.'
            }
            return jsonify(response), 400
        
        name = request.args.get('name')
        if (name is None):
            response = {
                'error': 'Missing name query parameter',
                'message': 'The parameter is required in the name query.'
            }
            return jsonify(response), 400
        
        item_id = request.args.get('itemId')
        if (item_id is None):
            response = {
                'error': 'Missing name item id parameter',
                'message': 'The parameter is required in the item id query.'
            }
            return jsonify(response), 400
        
        html_body = html_body.replace('{name}', name)
        html_body = html_body.replace('{item_id}', item_id)

        #Formatting 
        em = EmailMessage()
        em['From'] = sender_email
        em['To'] = email
        em['Subject'] = "SavvyShopper: Item reached your desired price"
        em.set_content(html_body, subtype='html')

        #extra security 
        ssl.create_default_context()

        #sends Email 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, em.as_string())
        server.quit() 

        return jsonify({"success": True, "message": "price reached email sent successfully"}), 200

    except FileNotFoundError:
        return jsonify({"success": False, "message": "Template file not found"}), 404
    except smtplib.SMTPException as e:
        return jsonify({"success": False, "message": f"Failed to send email: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

def about():
    return 'About'