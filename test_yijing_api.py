#!/usr/bin/env python3
"""
Simple Flask app to test the Yi Jing phone number functionality
"""

from flask import Flask, request, jsonify
from app.yijing import phone_to_hexagram_json
import json

app = Flask(__name__)

@app.route('/api/yijing/phone', methods=['GET'])
def yijing_phone():
    phone_number = request.args.get('phone', '')
    if not phone_number:
        return jsonify({
            "success": False,
            "error": "Phone number is required"
        })
    
    try:
        # Get the Yi Jing hexagram for the phone number
        result = phone_to_hexagram_json(phone_number)
        # Parse the JSON string to a Python object
        result_obj = json.loads(result)
        return jsonify(result_obj)
    except Exception as e:
        return jsonify({
            "success": False,
            "phone_number": phone_number,
            "error": str(e)
        })

if __name__ == '__main__':
    print("Starting local server for testing Yi Jing phone API...")
    print("Test the API with: http://localhost:5000/api/yijing/phone?phone=12345678")
    app.run(debug=True) 