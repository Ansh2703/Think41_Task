# routes.py

from flask import Blueprint, request, jsonify
from models import db, User, Connection

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(user_str_id=data['user_str_id'], display_name=data['display_name'])
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "internal_db_id": user.id,
        "user_str_id": user.user_str_id,
        "status": "created"
    }), 201

@api_blueprint.route('/connections', methods=['POST'])
def create_connection():
    data = request.json
    user1 = User.query.filter_by(user_str_id=data['user1_str_id']).first()
    user2 = User.query.filter_by(user_str_id=data['user2_str_id']).first()

    if not user1 or not user2:
        return jsonify({"error": "User not found"}), 404

    uid1, uid2 = sorted([user1.id, user2.id])
    existing = Connection.query.filter_by(user1_id=uid1, user2_id=uid2).first()
    if existing:
        return jsonify({"error": "Connection already exists"}), 409

    connection = Connection(user1_id=uid1, user2_id=uid2)
    db.session.add(connection)
    db.session.commit()
    return jsonify({"status": "connection_added"}), 201

@api_blueprint.route('/users/<user_str_id>/friends', methods=['GET'])
def get_friends(user_str_id):
    user = User.query.filter_by(user_str_id=user_str_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    connections = Connection.query.filter(
        (Connection.user1_id == user.id) | (Connection.user2_id == user.id)
    ).all()

    friends = []
    for conn in connections:
        friend_id = conn.user2_id if conn.user1_id == user.id else conn.user1_id
        friend = User.query.get(friend_id)
        friends.append({"user_str_id": friend.user_str_id, "display_name": friend.display_name})

    return jsonify(friends), 200

@api_blueprint.route('/connections', methods=['DELETE'])
def delete_connection():
    data = request.json
    user1 = User.query.filter_by(user_str_id=data['user1_str_id']).first()
    user2 = User.query.filter_by(user_str_id=data['user2_str_id']).first()

    if not user1 or not user2:
        return jsonify({"error": "User not found"}), 404

    uid1, uid2 = sorted([user1.id, user2.id])
    conn = Connection.query.filter_by(user1_id=uid1, user2_id=uid2).first()

    if not conn:
        return jsonify({"error": "Connection does not exist"}), 404

    db.session.delete(conn)
    db.session.commit()
    return jsonify({"status": "connection_removed"}), 200

@api_blueprint.route('/users/<user_str_id>/friends-of-friends', methods=['GET'])
def friends_of_friends(user_str_id):
    user = User.query.filter_by(user_str_id=user_str_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    connections = Connection.query.filter(
        (Connection.user1_id == user.id) | (Connection.user2_id == user.id)
    ).all()
    direct_friends = set()
    for conn in connections:
        fid = conn.user2_id if conn.user1_id == user.id else conn.user1_id
        direct_friends.add(fid)

    second_degree = set()
    for friend_id in direct_friends:
        f_conns = Connection.query.filter(
            (Connection.user1_id == friend_id) | (Connection.user2_id == friend_id)
        ).all()
        for f_conn in f_conns:
            fid = f_conn.user2_id if f_conn.user1_id == friend_id else f_conn.user1_id
            if fid != user.id and fid not in direct_friends:
                second_degree.add(fid)

    result = []
    for fid in second_degree:
        friend = User.query.get(fid)
        result.append({"user_str_id": friend.user_str_id, "display_name": friend.display_name})
    return jsonify(result), 200

@api_blueprint.route('/connections/degree', methods=['GET'])
def degree_of_separation():
    from_id = request.args.get('from_user_str_id')
    to_id = request.args.get('to_user_str_id')

    from_user = User.query.filter_by(user_str_id=from_id).first()
    to_user = User.query.filter_by(user_str_id=to_id).first()
    if not from_user or not to_user:
        return jsonify({"message": "User not found"}), 404

    from collections import deque
    visited = set()
    queue = deque([(from_user.id, 0)])

    while queue:
        current, degree = queue.popleft()
        if current == to_user.id:
            return jsonify({"degree": degree})

        visited.add(current)
        connections = Connection.query.filter(
            (Connection.user1_id == current) | (Connection.user2_id == current)
        ).all()

        for conn in connections:
            neighbor = conn.user2_id if conn.user1_id == current else conn.user1_id
            if neighbor not in visited:
                queue.append((neighbor, degree + 1))
                visited.add(neighbor)

    return jsonify({"degree": -1, "message": "not_connected"}), 200
