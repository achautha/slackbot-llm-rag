import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from download_judgements import show_cases

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.command("/get-case-digest")
def get_case_digest(ack, respond, command):
    # Acknowledge command request
    ack()
    cases = show_cases()
    print(cases)
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"We found *{len(cases)}* cases today!"},
        },
        {
            "type": "divider"
        },
    ]

    for case in cases:
        blocks = blocks + [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{case['link']}| {case['title']}>*\nDiary no: {case['diary_no']}",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Summarize a case",
                        "emoji": True
                    },
                    "value": case['diary_no'],
                    "action_id": "button-action"
                }
            },
            {
                "type": "divider"
            },
        ]
    respond(text=f"{command['text']}", blocks=blocks)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
