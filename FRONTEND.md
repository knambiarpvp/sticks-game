# Sticks Game - Frontend

A graphical, interactive web-based frontend for the classic Sticks game.

## Features

- **Visual Hand Representation**: Each hand is displayed as SVG with fingers representing the number of "sticks" (0-5)
- **Drag & Drop Attacks**: Drag your hand over opponent's hands to attack them
- **Button-Based Actions**: 
  - Attack: Select an opponent's hand to attack
  - Redistribute: Move sticks between your own hands (with custom amounts)
- **Real-Time Game State**: Visual feedback showing active hands, eliminated hands, and turn indicators
- **Multiplayer Support**: Two-player local gameplay
- **Responsive Design**: Works on desktop and mobile devices

## How to Play

1. **Open the Game**: Open `index.html` in your web browser
2. **Enter Player Names**: Input the names for both players and click "Start Game"
3. **Take Your Turn**: On your turn, you can:
   - **Attack**: Click "Attack" button, select which of your hands attacks which opponent hand
   - **Redistribute**: Click "Redistribute" button, select how many sticks to move between your hands
   - **Drag & Drop Attack** (Alternative): Drag one of your hands onto an opponent's hand to attack

## Game Rules

- Each player starts with 1 stick in each hand (2 hands total)
- On your turn, choose to:
  - **Attack**: Transfer all sticks from one of your hands to one of opponent's hands
  - **Redistribute**: Move any amount of sticks from one of your hands to your other hand
- Hands with more than 5 sticks are eliminated (become 0 sticks)
- Game ends when one player has both hands eliminated (0 sticks in both hands)
- The last player with at least one active hand wins!

## Files

- `index.html` - Game interface and structure
- `styles.css` - Visual styling and responsive layout
- `game.js` - Core game logic (mirrors Python backend)
- `ui.js` - User interface handling and interactions

## Browser Compatibility

Works on all modern browsers supporting:
- HTML5 and CSS3
- ES6 JavaScript
- SVG
- Drag & Drop API

## Technical Details

### Hand Display
- Hands are rendered as SVG with an ellipse palm
- Fingers/sticks are drawn as rounded rectangles
- Number of fingers matches the stick count (0-5)
- Eliminated hands show a grayed-out palm with no fingers

### Interactions
- **Click Actions**: Buttons for attack and redistribute
- **Drag & Drop**: Left-click and drag your hand to opponent's hand to attack
- **Input Prompts**: When redistributing, select the amount to move with an input slider

### Game State
- All game logic runs client-side in JavaScript
- State is managed in the `Game` class in `game.js`
- UI updates whenever the game state changes
