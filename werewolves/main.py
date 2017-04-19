import json
from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from google.cloud import datastore


app = Flask(__name__)
CORS(app)
ds_client = datastore.Client("werewolf-api")


@app.route('/api/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)

    key = ds_client.key('User')

    user = datastore.Entity(key)

    user.update({
        'username': username,
        'password': password
    })

    ds_client.put(user)

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)

    query = ds_client.query(kind='User')
    query.add_filter('username', '=', username)
    query.add_filter('password', '=', password)

    results = list(query.fetch())

    if not results:
        return jsonify({'result': 'fail'})

    user = results[0]

    return jsonify({'result': 'success', 'user_id': user.key.id})


@app.route('/api/room', methods=['POST'])
def create_room():
    user_id = request.json.get('user_id')
    if user_id is None:
        abort(400)

    key = ds_client.key('Room')
    room = datastore.Entity(key)

    room.update({
        'players': [
            json.dumps({'user_id': user_id, 'role': "", 'points': 0})
        ]
    })

    ds_client.put(room)

    return jsonify({'result': 'success', 'room': room.key.id})


@app.route('/api/room/<room_id>/player', methods=['POST'])
def add_player(room_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        abort(400)

    with ds_client.transaction():
        key = ds_client.key('Room', int(room_id))
        room = ds_client.get(key)

        if not room:
            return jsonify({'result': 'fail'})

        room['players'].append(json.dumps({'user_id': user_id, 'role': "", 'points': 0}))

        ds_client.put(room)

    return jsonify({'result': 'success'})


@app.route('/api/room/<room_id>/player/<user_id>/role', methods=['POST'])
def add_role(room_id, user_id):
    role = request.json.get('role')
    if role is None:
        abort(400)

    with ds_client.transaction():
        key = ds_client.key('Room', int(room_id))
        room = ds_client.get(key)

        if not room:
            return jsonify({'result': 'fail'})

        for i, json_player in enumerate(room['players']):
            player = json.loads(json_player)
            if player['user_id'] == user_id:
                player['role'] = role
                room['players'][i] = json.dumps(player)
                break

        ds_client.put(room)

    return jsonify({'result': 'success'})


@app.route('/api/room/<room_id>/<winner>', methods=['POST'])
def submit(room_id, winner):
    with ds_client.transaction():
        key = ds_client.key('Room', int(room_id))
        room = ds_client.get(key)

        if not room:
            return jsonify({'result': 'fail'})

        players = [json.loads(json_player) for json_player in room['players']]
        for player in players:
            if player['role'] == 'werewolf' and winner == 'werewolf':
                player['points'] += 40
            if (player['role'] == 'villager' or player['role'] == 'shuffle') and winner == 'shuffle':
                player['points'] += 20
            player['role'] = ''

        for i, player in enumerate(players):
            room['players'][i] = json.dumps(player)

        ds_client.put(room)

    return jsonify({'result': 'success'})


@app.route('/api/room/<room_id>/players', methods=['GET'])
def room_players(room_id):
    key = ds_client.key('Room', int(room_id))
    room = ds_client.get(key)

    if not room:
        return jsonify({'result': 'fail'})

    players = [json.loads(json_player) for json_player in room['players']]

    return jsonify({'result': 'success', 'data': players})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

