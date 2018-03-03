import config
import os
import time
from slackclient import SlackClient

BOT_ACCESS_TOKEN = config.BOT_ACCESS_TOKEN

class SlackBot(object):
    '''
    This is a wrapper for the slackclient library that you can use if you find
    helpful. Add methods as you see fit. Only a bot access token that starts
    with xoxb needs to be provided as an input argument.
    '''
    def __init__(self, access_token):
        self.sc = SlackClient(access_token)

    def rtm_socket_connected(self):
        '''
        Checks if the bot is connected to the real time messaging socket, which
        allows it to monitor messages in the slack in real-time.
        '''
        return self.sc.rtm_connect()

    def send_message(self, message, channel):
        '''
        Sends a message to a channel. The message can be a formatted markdown
        message. The channel can be a DM, MPDM (multiple person DM), or a public
        or private channel.
        '''
        res = self.sc.api_call("chat.postMessage", channel=channel, text=message)
        return res

    def read_rtm_messages(self):
        '''
        Reads the incoming stream of real time messages from all channels the
        bot is a member of.
        '''
        res = self.sc.rtm_read()
        return res

    def handle_event(self, rtm_event):
        '''
        Handles all real time messaging events.
        '''
        if len(rtm_event) == 0:
            return

        event = rtm_event[0]

        # Right now, just handles the case where it replies to any message that
        # says "hello" with "hello there"
        if "type" in event and event["type"] == "message":
            channel = event["channel"]
            message = event["text"]
            if message == "hello":
                print("message sent was hello")
                self.send_message("hello there", channel)

            elif message == "What are we building today?":
                print("asked about project")
                self.send_message("""
                We are buidling a slack bot that can automatically
                schedule and display events to a shared google calendar
                right through slack!""",channel)

            elif message == "Let me authorize my account":
                print("asking for authentication")
                self.send_message(""" Please authenticate your account here:
                https://slack.com/oauth/authorize""",channel)

    def activate(self):
        '''
        Starts the bot, which monitors all messages events from channels it is a
        part of and then sends them to the message handler.
        '''
        if self.rtm_socket_connected():
            print("Bot is up and running\n")
            while True:
                try:
                    self.handle_event(self.read_rtm_messages())
                except:
                    continue
        else:
            print("Error, check access token!")

if __name__ == "__main__":
    bot = SlackBot(BOT_ACCESS_TOKEN)
    bot.activate()
