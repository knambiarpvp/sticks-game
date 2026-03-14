# sticks-game
A simple implementation of the classic game of sticks as a browser game

## Running the Game

### Requirements
- Python 3.7+
- Flask 2.3+

### Setup
1. Install dependencies:
```bash
pip install -r server/requirements.txt
```

2. Start the Flask server from the project root:
```bash
python server/app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
sticks-game/
├── frontend/                    # Frontend files
│   ├── index.html              # Game interface
│   ├── styles.css              # Styling
│   └── ui.js                   # Frontend interactions
├── server/                      # Backend Flask server
│   ├── app.py                  # Flask REST API
│   ├── sticks_game_backend.py  # Core game logic
│   ├── test_backend.py         # Test suite
│   └── requirements.txt        # Python dependencies
├── README.md                    # This file
├── FRONTEND.md                  # Frontend documentation
└── FLASK.md                     # Backend API documentation
```

## Architecture

The game consists of:
- **Backend**: Flask REST API server handling all game logic
- **Frontend**: HTML/CSS/JavaScript providing the user interface
- **Communication**: JSON REST API between frontend and backend

### API Endpoints
- `POST /api/game/new` - Create a new game
- `GET /api/game/<game_id>` - Get game state
- `POST /api/game/<game_id>/attack` - Execute an attack
- `POST /api/game/<game_id>/redistribute` - Execute a redistribution

## Game Rules
- Each player starts with 1 stick in each hand
- On your turn, choose to:
  - **Attack**: Transfer all sticks from one of your hands to opponent's hand
  - **Redistribute**: Move sticks between your own hands (partial or full)
- Hands with more than 5 sticks are eliminated (0 sticks)
- Game ends when one player has both hands eliminated
- The last player with at least one active hand wins!

## Development

### Running Tests
```bash
python server/test_backend.py
```

### Backend Documentation
See [FLASK.md](FLASK.md) for detailed API documentation and backend information.

### Frontend Documentation
See [FRONTEND.md](FRONTEND.md) for frontend implementation details.