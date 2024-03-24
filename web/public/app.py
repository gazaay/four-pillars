from flask import Flask, render_template,request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    # Parse the JSON payload from the request
    data = request.json

    # Extract the values from the JSON payload
    symbol = data.get('symbol')
    close = data.get('close')
    time = data.get('time')
    action = data.get('action')

    # Process the data as needed (e.g., send it to a database, trigger notifications)
    # For demonstration purposes, let's just print the data
    print("Received webhook:")
    print("Symbol:", symbol)
    print("Close:", close)
    print("Time:", time)
    print("Action:", action)

    # Optionally, send a response back to TradingView to acknowledge receipt of the webhook
    # You can customize the response message as needed
    response = {'message': 'Webhook received successfully'}
    return jsonify(response), 200
    
if __name__ == '__main__':
    app.run(debug=True)
