"""
Sticks Game - Flask Backend

A Flask application serving the Sticks game API.
Uses the Python game logic from sticks_game_backend.py
"""

import os
import sys
from flask import Flask, jsonify, request, render_template

# Add the server directory to Python path to import local modules
sys.path.insert(0, os.path.dirname(__file__))

from sticks_game_backend import Game, Player
import json

# Get the path to the frontend directory (one level up and then into frontend)
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

app = Flask(__name__, 
            static_folder=frontend_dir,
            static_url_path='',
            template_folder=frontend_dir)

# Store active games by session ID
games = {}
game_counter = 0


def serialize_player(player):
    """Convert a Player object to JSON-serializable dict."""
    return {
        'name': player.name,
        'leftHand': player.left_hand,
        'rightHand': player.right_hand,
        'isEliminated': player.is_eliminated(),
        'hasActiveHands': player.has_active_hands()
    }


def serialize_game(game):
    """Convert a Game object to JSON-serializable dict."""
    return {
        'player1': serialize_player(game.player1),
        'player2': serialize_player(game.player2),
        'currentPlayer': game.current_player.name,
        'otherPlayer': game.other_player.name,
        'gameOver': game.game_over,
        'winner': game.winner.name if game.winner else None
    }


@app.route('/')
def index():
    """Serve the main game page."""
    return render_template('index.html')


@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Create a new game."""
    global game_counter
    
    data = request.json
    player1_name = data.get('player1Name', 'Player 1')
    player2_name = data.get('player2Name', 'Player 2')
    
    game_id = f'game_{game_counter}'
    game_counter += 1
    
    game = Game(player1_name, player2_name, initial_sticks=1)
    games[game_id] = game
    
    return jsonify({
        'gameId': game_id,
        'gameState': serialize_game(game),
        'validActions': get_valid_actions_dict(game)
    })


@app.route('/api/game/<game_id>', methods=['GET'])
def get_game_state(game_id):
    """Get the current state of a game."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    return jsonify({
        'gameState': serialize_game(game),
        'validActions': get_valid_actions_dict(game)
    })


def get_valid_actions_dict(game):
    """Convert valid actions to a JSON-serializable format."""
    actions = game.get_valid_actions()
    
    return {
        'attack': [
            {
                'source': action[0],
                'target': action[1],
                'sourceSticks': game.current_player.left_hand if action[0] == 'left' else game.current_player.right_hand,
                'targetSticks': game.other_player.left_hand if action[1] == 'left' else game.other_player.right_hand
            }
            for action in actions['attack']
        ],
        'redistribute': [
            {
                'from': action[0],
                'to': action[1],
                'maxAmount': game.current_player.left_hand if action[0] == 'left' else game.current_player.right_hand
            }
            for action in actions['redistribute']
        ]
    }


@app.route('/api/game/<game_id>/attack', methods=['POST'])
def execute_attack(game_id):
    """Execute an attack action."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    data = request.json
    
    source_hand = data.get('sourceHand')
    target_hand = data.get('targetHand')
    
    if not source_hand or not target_hand:
        return jsonify({'error': 'Missing sourceHand or targetHand'}), 400
    
    # Execute the attack
    success = game.execute_attack(source_hand, target_hand)
    
    if not success:
        return jsonify({'error': 'Invalid attack'}), 400
    
    return jsonify({
        'success': True,
        'gameState': serialize_game(game),
        'validActions': get_valid_actions_dict(game)
    })


@app.route('/api/game/<game_id>/redistribute', methods=['POST'])
def execute_redistribute(game_id):
    """Execute a redistribute action."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    data = request.json
    
    from_hand = data.get('fromHand')
    to_hand = data.get('toHand')
    amount = data.get('amount')
    
    if not from_hand or not to_hand or amount is None:
        return jsonify({'error': 'Missing fromHand, toHand, or amount'}), 400
    
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Execute the redistribution
    success = game.execute_redistribute(from_hand, to_hand, amount)
    
    if not success:
        return jsonify({'error': 'Invalid redistribution'}), 400
    
    return jsonify({
        'success': True,
        'gameState': serialize_game(game),
        'validActions': get_valid_actions_dict(game)
    })


if __name__ == '__main__':
    app.run(debug=True, port=8081)
