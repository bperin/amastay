from flask import Flask, request, jsonify
from controllers.scrape_controller import handle_scrape
from controllers.chat_controller import handle_chat

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    return handle_scrape(request)

@app.route('/chat', methods=['POST'])
def chat():
    return handle_chat(request)

if __name__ == "__main__":
    app.run(debug=True)
