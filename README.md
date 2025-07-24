# Social Connections API (Friendship Management)

This project is an API to manage users, friendships, and connections like a basic social network. It supports:

- User creation
- Friendship creation & deletion
- Fetching friends and friends-of-friends
- Finding degrees of separation using BFS

## Tech Stack

- Python 3
- Flask
- SQLAlchemy
- SQLite (for now, easily replaceable with MySQL/PostgreSQL)

## API Endpoints

- `POST /users`: Create user
- `POST /connections`: Create friendship
- `DELETE /connections`: Remove friendship
- `GET /users/<user_str_id>/friends`: List friends
- `GET /users/<user_str_id>/friends-of-friends`: List 2nd-degree connections
- `GET /connections/degree?from_user_str_id=A&to_user_str_id=B`: Degree of separation (BFS)

## How to Run

```bash
pip install -r requirements.txt
python app.py
