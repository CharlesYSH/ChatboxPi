from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import Chatbot.chatbot as Chatbot

chatter = Chatbot.Chatbot()
#parser = reqparse.RequestParser()
#parser.add_argument('task')

app = Flask(__name__)
api = Api(app)

class TodoList(Resource):
    def get(self):
        return "TAKE A REST"

    def post(self):
        json_data = request.get_json(force=True)
        get_text = str(json_data['task'])
        print(get_text)
        TODOS = self.handler(get_text)
        return TODOS, 201

    def handler(self, get_text):
        get_text = chatter.waiting_loop(get_text)
        return {'Result': get_text }

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/chat')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
