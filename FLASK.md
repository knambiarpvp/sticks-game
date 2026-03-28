# Sticks Game - Flask Backend

A Flask REST API backend for the Sticks game. This serves the game logic and provides endpoints for the web frontend to communicate with.

## Running the Server

### Prerequisites
- Python 3.7+
- Dependencies: `pip install -r requirements.txt`

### Starting the Server

```bash
cd c:\Dev\sticks-game
pip install -r requirements.txt
python app.py
```

The server will start on `http://localhost:5000`

### Production Deployment

For production use, replace the Flask development server with a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 app:app
```

## API Endpoints

### Create a New Game
**POST** `/api/game/new`

Request:
```json
{
  "player1Name": "Alice",
  "player2Name": "Bob"
}
```

Response:
```json
{
  "gameId": "game_0",
  "gameState": {
    "player1": {
      "name": "Alice",
      "leftHand": 1,
      "rightHand": 1,
      "isEliminated": false,
      "hasActiveHands": true
    },
    "player2": {
      "name": "Bob",
      "leftHand": 1,
      "rightHand": 1,
      "isEliminated": false,
      "hasActiveHands": true
    },
    "currentPlayer": "Alice",
    "otherPlayer": "Bob",
    "gameOver": false,
    "winner": null
  },
  "validActions": {
    "attack": [
      {
        "source": "left",
        "target": "left",
        "sourceSticks": 1,
        "targetSticks": 1
      }
    ],
    "redistribute": [
      {"from": "left", "to": "right", "maxAmount": 1},
      {"from": "right", "to": "left", "maxAmount": 1}
    ]
  }
}
```

### Get Game State
**GET** `/api/game/<game_id>`

Response: Same as the `gameState` and `validActions` from create game endpoint

### Execute Attack
**POST** `/api/game/<game_id>/attack`

Request:
```json
{
  "sourceHand": "left",
  "targetHand": "right"
}
```

Response: Returns updated `gameState` and `validActions`

### Execute Redistribution
**POST** `/api/game/<game_id>/redistribute`

Request:
```json
{
  "fromHand": "left",
  "toHand": "right",
  "amount": 1
}
```

Response: Returns updated `gameState` and `validActions`

## Architecture

The Flask backend:
1. Imports the `Game` and `Player` classes from `sticks_game_backend.py`
2. Maintains game state in a dictionary (one entry per game session)
3. Serializes game state to JSON for API responses
4. Validates all moves before executing them

Games are stored in memory and will be lost when the server restarts. For persistent game storage, add a database layer.

## Game Logic

All game logic is delegated to the `Game` class in `sticks_game_backend.py`. The Flask app simply:
- Manages game sessions
- Serializes/deserializes game state
- Routes API requests to the appropriate game methods
- Returns JSON responses

## Error Handling

API errors return appropriate HTTP status codes:
- `404` - Game not found
- `400` - Invalid request (missing parameters, invalid action)
- `500` - Server error

## Testing

Run the backend tests:
```bash
python test_backend.py
```

Test API endpoints with curl:
```bash
# Create game
curl -X POST http://localhost:5000/api/game/new \
  -H "Content-Type: application/json" \
  -d '{"player1Name": "Alice", "player2Name": "Bob"}'

# Get game state
curl http://localhost:5000/api/game/game_0

# Attack
curl -X POST http://localhost:5000/api/game/game_0/attack \
  -H "Content-Type: application/json" \
  -d '{"sourceHand": "left", "targetHand": "right"}'
```

## Integration with Frontend

The frontend (`ui.js`) communicates with this backend via the REST API:
- Calls `/api/game/new` to start a new game
- Calls `/api/game/<id>/attack` and `/api/game/<id>/redistribute` for actions
- Displays the returned game state in the UI
- Shows valid actions to the player based on the API response
