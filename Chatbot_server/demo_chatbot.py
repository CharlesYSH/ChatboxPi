import Chatbot.chatbot as Chatbot

chatter = Chatbot.Chatbot()
while True:
    in_text = input(">> ")
    out_text = chatter.waiting_loop(in_text)