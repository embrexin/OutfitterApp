from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import uuid
from weather import get_current_weather
from suggester import suggest_outfit_for_api

app = Flask(__name__)
CORS(app)

CLOTHING_FILE_PATH = '../src/assets/clothing/clothing.json'
EVENTS_FILE_PATH = './events.json'

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/api/events')
def get_events():
    data = read_json_file(EVENTS_FILE_PATH)
    return jsonify(data)

@app.route('/api/event/<event_id>')
def get_event(event_id):
    events = read_json_file(EVENTS_FILE_PATH)
    event = next((event for event in events if event.get('id') == event_id), None)
    if event:
        return jsonify(event)
    return jsonify({'message': 'Event not found'}), 404

@app.route('/api/add-event', methods=['POST'])
def add_event():
    new_event = request.get_json()
    new_event['id'] = str(uuid.uuid4())
    events = read_json_file(EVENTS_FILE_PATH)
    events.append(new_event)
    write_json_file(EVENTS_FILE_PATH, events)
    return jsonify({'message': 'Event added successfully', 'event': new_event})

@app.route('/api/update-event/<event_id>', methods=['PUT'])
def update_event(event_id):
    updated_event = request.get_json()
    events = read_json_file(EVENTS_FILE_PATH)
    for i, event in enumerate(events):
        if event.get('id') == event_id:
            updated_event['id'] = event_id
            events[i] = updated_event
            write_json_file(EVENTS_FILE_PATH, events)
            return jsonify({'message': 'Event updated successfully', 'event': updated_event})
    return jsonify({'message': 'Event not found'}), 404

@app.route('/api/delete-event/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    events = read_json_file(EVENTS_FILE_PATH)
    event_to_delete = next((event for event in events if event.get('id') == event_id), None)
    if event_to_delete:
        events.remove(event_to_delete)
        write_json_file(EVENTS_FILE_PATH, events)
        return jsonify({'message': 'Event deleted successfully'})
    return jsonify({'message': 'Event not found'}), 404

@app.route('/api/clothing')
def get_clothing():
    data = read_json_file(CLOTHING_FILE_PATH)
    return jsonify(data)

@app.route('/api/clothing/manual-upload', methods=['POST'])
def manual_upload_clothing():
    """
    Upload clothing item with manual classification (no API needed)
    """
    try:
        data = request.get_json()

        if not data or 'category' not in data or 'image' not in data:
            return jsonify({'error': 'Missing category or image data'}), 400

        category = data['category']
        tags = data.get('tags', [])
        image_base64 = data['image']

        # Get current clothing data
        clothing_data = read_json_file(CLOTHING_FILE_PATH)

        # Generate new ID
        max_id = max([item['id'] for item in clothing_data]) if clothing_data else 0
        new_id = max_id + 1

        # Create new clothing item
        new_item = {
            "id": new_id,
            "label": category.capitalize(),
            "name": category.capitalize(),
            "src": f"./uploaded_{new_id}.jpg",
            "image": image_base64,  # Store base64 image data
            "alt": category,
            "tags": tags
        }

        # Add to clothing data
        clothing_data.append(new_item)
        write_json_file(CLOTHING_FILE_PATH, clothing_data)

        return jsonify({
            'message': 'Clothing item added successfully',
            'item': {
                'id': new_id,
                'name': category.capitalize(),
                'category': category
            }
        }), 200

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/clothing/<int:item_id>/save', methods=['POST'])
def save_item(item_id):
    clothing_data = read_json_file(CLOTHING_FILE_PATH)
    item_found = False
    for item in clothing_data:
        if item['id'] == item_id:
            if 'saved' not in item['tags']:
                item['tags'].append('saved')
            item_found = True
            break
    if item_found:
        write_json_file(CLOTHING_FILE_PATH, clothing_data)
        return jsonify({'message': 'Item saved successfully'})
    return jsonify({'message': 'Item not found'}), 404

@app.route('/api/clothing/<int:item_id>/unsave', methods=['POST'])
def unsave_item(item_id):
    clothing_data = read_json_file(CLOTHING_FILE_PATH)
    item_found = False
    for item in clothing_data:
        if item['id'] == item_id:
            if 'saved' in item['tags']:
                item['tags'].remove('saved')
            item_found = True
            break
    if item_found:
        write_json_file(CLOTHING_FILE_PATH, clothing_data)
        return jsonify({'message': 'Item unsaved successfully'})
    return jsonify({'message': 'Item not found'}), 404

@app.route('/api/wear-items', methods=['POST'])
def wear_items():
    data = request.get_json()
    worn_item_ids = data.get('item_ids', [])

    clothing_data = read_json_file(CLOTHING_FILE_PATH)

    # Remove 'recently worn' tag from all items
    for item in clothing_data:
        if 'recently worn' in item['tags']:
            item['tags'].remove('recently worn')

    # Add 'recently worn' tag to the new items
    for item in clothing_data:
        if item['id'] in worn_item_ids:
            if 'recently worn' not in item['tags']:
                item['tags'].append('recently worn')

    write_json_file(CLOTHING_FILE_PATH, clothing_data)

    return jsonify({'message': 'Clothing updated successfully'})

@app.route('/api/weather')
def weather():
    weather_data = get_current_weather()
    if weather_data is not None:
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'Could not retrieve weather data'}), 500

@app.route('/api/suggest-outfit')
def suggest_outfit():
    """
    Generate smart outfit suggestion based on weather and clothing inventory
    """
    try:
        # Get current weather
        weather_data = get_current_weather()
        if weather_data is None:
            return jsonify({'error': 'Could not retrieve weather data'}), 500

        # Get clothing inventory
        clothing_data = read_json_file(CLOTHING_FILE_PATH)

        # Generate suggestion
        suggestion = suggest_outfit_for_api(clothing_data, weather_data)

        return jsonify(suggestion)

    except Exception as e:
        print(f"Error generating outfit suggestion: {str(e)}")
        return jsonify({'error': 'Failed to generate outfit suggestion'}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
