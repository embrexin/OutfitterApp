from flask import Flask, jsonify
from weather import get_current_temp_f

app = Flask(__name__)

@app.route('/api/weather')
def weather():
    temp = get_current_temp_f()
    if temp is not None:
        return jsonify({'temperature': temp})
    else:
        return jsonify({'error': 'Could not retrieve weather data'}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
