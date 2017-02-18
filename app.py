import os
import sys
import json
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Go Go Power Ranger V5", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if messaging_event["message"].get("text"):
                        message_text = messaging_event["message"]["text"]  # the message's text
                        send_message(sender_id, message_text)
                    else:
                        #message_text ='Opps, no picture!'
                        send_image(sender_id)
                    #send_message(sender_id, message_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
def send_image(recipient_id):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message":{
            "attachment":{
                "type":"image",
                "payload":{
                    "url":"http://ansi.loli.tw/ansiarts/4846.png"
                }
            }
        }
    })
    i = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if i.status_code != 200:
        log(i.status_code)
        log(i.text)

"""
def get_start(USER_DEFINED_PAYLOAD):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "setting_type":"call_to_actions",
        "thread_state":"new_thread",
        "call_to_actions":[
            {
                "payload":USER_DEFINED_PAYLOAD
            }
        ]
    })
    g = requests.post("https://graph.facebook.com/v2.6/me/thread_settings",params=params,headers=headers,data=data)
    if g.status_code !=200:
        log(g.status_code)
        log(g.text)
"""
def log(message):  # simple wrapper for logging to stdout on heroku
    print (str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
