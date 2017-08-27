# -*- coding: utf-8 -*-
import json, time, pprint
import bot
from collections import defaultdict
from flask import Flask, request, make_response, render_template, jsonify


pp = pprint.PrettyPrinter(indent=4)
pyBot = bot.Bot()

app = Flask(__name__)

@app.route("/begin_auth", methods=["GET"])
def preInstall():
    client_id = pyBot.oauth["client_id"]
    oauth_scope = pyBot.oauth["scope"]
    return render_template("install.html", scope=oauth_scope, client_id=client_id)

@app.route("/finish_auth", methods=["GET", "POST"])
def postInstall():
    """
    Retrieve the auth code from the request params and request the auth tokens from Slack.
    """
    auth_code = request.args['code']
    pyBot.auth(auth_code)
    return render_template("thanks.html")

@app.route("/event_listening", methods=["GET", "POST"])
def eventListening():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)
    # print('slack_event =')
    # pp.pprint(slack_event)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200,
                             {"content_type": "application/json"})

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/command_listening", methods=["POST"])
def commandListening():
    # get the key/value pairs in the body from a HTML post form
    token = request.form.get("token", None)
    command = request.form.get("command", None)
    text = request.form.get("text", None)
    user_id = request.form.get("user_id", None)
    user_name = request.form.get("user_name", None)
    channel_id = request.form.get("channel_id", None)
    DMchannel_id = getDMChannelId(user_id) # direct message channel id

    if command == "/truth":
        pyBot.targetChannel = channel_id
        post_message = pyBot.client.api_call("chat.postMessage",
                            channel=channel_id,
                            as_user=True,
                            text="%s used */truth*" % user_name
                            )
        if not post_message["ok"]:
            pp.pprint(post_message)

        # Send direct message to each member in the channel
        all_members = getMembers(channel_id)
        attachment_members = [{"text": memb, "value": memb} for memb in all_members.keys()]
        for member_id in all_members.values():
            post_message = pyBot.client.api_call("chat.postMessage",
                                channel=getDMChannelId(member_id),
                                as_user=True,
                                text="Who is the man you want to kick out of your team?:smiling_imp:",
                                attachments=[
                                    {
                                        "fallback": "Please update your Slack client.",
                                        "attachment_type": "default",
                                        "callback_id": "members_selection",
                                        "actions": [
                                            {
                                                "name": "members_list",
                                                "text": "Select a member...",
                                                "type": "select",
                                                "options": attachment_members
                                            }
                                        ]
                                    }
                                ]
                                )
            if not post_message["ok"]:
                pp.pprint(post_message)
    return make_response("", 200,)

@app.route("/click_listening", methods=["POST"])
def clickListening():
    # Parse the request payload
    data = json.loads(request.form["payload"])
    actions = data["actions"]
    original_message = data.get("original_message")
    user_name = data["user"]["name"]
    # pp.pprint(data)

    if actions[0]["name"] == "members_list" and pyBot.targetChannel != "":
        selected_option = actions[0]["selected_options"][0]["value"]
        message = "Sorry @%s, @%s wants you to leave:sob:" % (selected_option, user_name)
        post_message = pyBot.client.api_call("chat.postMessage",
                            channel=pyBot.targetChannel,
                            as_user=True,
                            text=message,
                            )
        if not post_message["ok"]:
            pp.pprint(post_message)
    
        # delete the original message
        post_message = pyBot.client.api_call("chat.delete",
                            channel=data["channel"]["id"],
                            ts=original_message["ts"]
                            )
        if not post_message["ok"]:
            pp.pprint(post_message)

    return make_response("", 200,) 

def _event_handler(event_type, slack_event):
    team_id = slack_event["team_id"]
    event_time = slack_event["event"]["ts"]
    channel_id = slack_event["event"]["channel"]
    subtype = slack_event["event"].get("subtype")
    user_id = slack_event["event"].get("user")
    bot_id = slack_event["event"].get("bot_id")
    text = slack_event["event"].get("text")
    # ============== Message Events ============= #
    if event_type == "message":
        if user_id and text:
            print("%s: %s [%s]" % (user_id, text, toDatetime(event_time)))

    return make_response("", 200,)

def getDMChannelId(user_id):
    """
    Get the direct message channel id of someone for the calling user (bot).
    """
    if not user_id:
        return None
    res = pyBot.client.api_call("im.list")
    if res["ok"]:
        for im in res["ims"]:
            if im["user"] == user_id:
                return im["id"]
    else:
        print("[Error in getDMChannelId: %s]" % res["error"])
    return None

def getUserName(user_id):
    if not user_id:
        return None
    res = pyBot.client.api_call("users.info", user=user_id)
    if res["ok"]:
        return res["user"]["name"]
    else:
        print("[Error in getUserName: %s]" % res["error"])
        return None

def getMembers(channel_id):
    if not channel_id:
        return {}
    res = pyBot.client.api_call("channels.info", channel=channel_id)
    if res["ok"]:
        members = {getUserName(user_id): user_id for user_id in res["channel"]["members"]}
        return members
    else:
        print("[Error in getMembers: %s]" % res["error"])
        return {}

def toDatetime(unix_ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(unix_ts)))


if __name__ == '__main__':
    app.run(debug=True)