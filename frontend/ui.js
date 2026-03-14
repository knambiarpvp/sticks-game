/**
 * Sticks Game - UI and Interactions
 * This file handles all UI rendering and user interactions
 * Communicates with Flask backend via REST API
 */

let gameId = null;
let gameState = null;
let validActions = null;
let draggedFromHand = null;
let draggedFromPlayer = null;

const API_BASE = '/api';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeGame();
    setupEventListeners();
});

function initializeGame() {
    const setupModal = document.getElementById('setup-modal');
    const startGameBtn = document.getElementById('start-game-btn');

    startGameBtn.addEventListener('click', async () => {
        const player1Name = document.getElementById('player1-input').value || 'Player 1';
        const player2Name = document.getElementById('player2-input').value || 'Player 2';

        try {
            const response = await fetch(`${API_BASE}/game/new`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    player1Name: player1Name,
                    player2Name: player2Name
                })
            });

            const data = await response.json();
            gameId = data.gameId;
            gameState = data.gameState;
            validActions = data.validActions;

            setupModal.style.display = 'none';
            updateGameDisplay();
            showMessage(`${gameState.currentPlayer} starts!`, 'info');
        } catch (error) {
            console.error('Error creating game:', error);
            showMessage('Failed to create game', 'error');
        }
    });
}

function setupEventListeners() {
    // Action buttons
    document.getElementById('attack-btn').addEventListener('click', showAttackPanel);
    document.getElementById('redistribute-btn').addEventListener('click', showRedistributePanel);
    document.getElementById('new-game-btn').addEventListener('click', resetGame);

    // Cancel buttons
    document.getElementById('cancel-attack-btn').addEventListener('click', hideActionPanels);
    document.getElementById('cancel-redistribute-btn').addEventListener('click', hideActionPanels);
    document.getElementById('cancel-amount-btn').addEventListener('click', hideActionPanels);

    // Confirm buttons
    document.getElementById('confirm-amount-btn').addEventListener('click', confirmAmount);

    // Game over modal
    document.getElementById('play-again-btn').addEventListener('click', resetGame);

    // Drag and drop setup
    setupDragAndDrop();
}

function setupDragAndDrop() {
    const hands = document.querySelectorAll('.hand');

    hands.forEach((hand) => {
        hand.addEventListener('dragstart', handleDragStart);
        hand.addEventListener('dragend', handleDragEnd);
        hand.addEventListener('dragover', handleDragOver);
        hand.addEventListener('dragleave', handleDragLeave);
        hand.addEventListener('drop', handleDrop);
    });
}

function handleDragStart(e) {
    if (!gameId) return;

    const handElement = e.target.closest('.hand');
    if (!handElement) return;

    const handId = handElement.id;
    const [player, hand] = parseHandId(handId);

    // Check if it's the current player's hand
    const isP1Turn = gameState.currentPlayer === gameState.player1.name;
    const isCurrentPlayerHand = (player === 'p1' && isP1Turn) || (player === 'p2' && !isP1Turn);

    if (!isCurrentPlayerHand) {
        e.preventDefault();
        return;
    }

    // Check if hand is eliminated
    const sticks = player === 'p1'
        ? (hand === 'left' ? gameState.player1.leftHand : gameState.player1.rightHand)
        : (hand === 'left' ? gameState.player2.leftHand : gameState.player2.rightHand);

    if (sticks === 0) {
        e.preventDefault();
        return;
    }

    draggedFromHand = hand;
    draggedFromPlayer = player;
    handElement.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'all';
    e.dataTransfer.setData('text/plain', handId);

    const playerName = player === 'p1' ? gameState.player1.name : gameState.player2.name;
    showMessage(`Dragging ${playerName}'s ${hand} hand...`, 'info');
}

function handleDragEnd(e) {
    const handElement = e.target.closest('.hand');
    if (handElement) {
        handElement.classList.remove('dragging');
    }
    draggedFromHand = null;
    draggedFromPlayer = null;
}

function handleDragOver(e) {
    if (draggedFromHand === null) return;

    const handElement = e.target.closest('.hand');
    if (!handElement) return;

    const [dropPlayer, dropHand] = parseHandId(handElement.id);

    // Allow drop on opponent's hands (attack) or own hands (redistribute)
    if (draggedFromPlayer === dropPlayer) {
        // Same player - can redistribute if different hand
        if (draggedFromHand !== dropHand) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            handElement.classList.add('drag-over');
        }
    } else {
        // Different player - can attack
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        handElement.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    const handElement = e.target.closest('.hand');
    if (handElement) {
        handElement.classList.remove('drag-over');
    }
}

async function handleDrop(e) {
    e.preventDefault();
    const handElement = e.target.closest('.hand');
    if (!handElement) return;

    handElement.classList.remove('drag-over');

    const [dropPlayer, dropHand] = parseHandId(handElement.id);

    // Check if source hand is eliminated
    const sourceSticks = draggedFromPlayer === 'p1'
        ? (draggedFromHand === 'left' ? gameState.player1.leftHand : gameState.player1.rightHand)
        : (draggedFromHand === 'left' ? gameState.player2.leftHand : gameState.player2.rightHand);

    if (sourceSticks === 0) {
        showMessage('Cannot use an eliminated hand!', 'error');
        draggedFromHand = null;
        draggedFromPlayer = null;
        return;
    }

    // Different player - Attack
    if (draggedFromPlayer !== dropPlayer) {
        try {
            const response = await fetch(`${API_BASE}/game/${gameId}/attack`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sourceHand: draggedFromHand,
                    targetHand: dropHand
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showMessage(data.error || 'Attack failed!', 'error');
                return;
            }

            gameState = data.gameState;
            validActions = data.validActions;

            const targetPlayerName = dropPlayer === 'p1' ? gameState.player1.name : gameState.player2.name;
            showMessage(`Attacked ${targetPlayerName}'s ${dropHand} hand!`, 'success');
            updateGameDisplay();

            if (gameState.gameOver) {
                showGameOverModal();
            } else {
                showMessage(`${gameState.currentPlayer}'s turn!`, 'info');
            }
        } catch (error) {
            console.error('Error executing attack:', error);
            showMessage('Failed to execute attack', 'error');
        }
    }
    // Same player - Redistribute
    else {
        if (draggedFromHand === dropHand) {
            showMessage('Select a different hand to redistribute!', 'error');
            draggedFromHand = null;
            draggedFromPlayer = null;
            return;
        }

        // Show amount input
        hideActionPanels();
        const amountPanel = document.getElementById('amount-panel');
        amountPanel.style.display = 'block';

        // Store redistribution context for amount confirmation
        const maxAmount = sourceSticks;
        window.redistributeData = {
            from: draggedFromHand,
            to: dropHand,
            max: maxAmount
        };

        // Set max amount
        const amountInput = document.getElementById('amount-input');
        amountInput.max = maxAmount;
        amountInput.value = 1;
        amountInput.min = 1;

        showMessage(`Move 1-${maxAmount} sticks from ${draggedFromHand} to ${dropHand}`, 'info');
    }

    draggedFromHand = null;
    draggedFromPlayer = null;
}

function parseHandId(handId) {
    // Format: "p1-left-hand" or "p2-right-hand"
    const parts = handId.split('-');
    return [parts[0], parts[1]]; // ['p1' or 'p2', 'left' or 'right']
}

function showAttackPanel() {
    if (!validActions || validActions.attack.length === 0) {
        showMessage('No valid attacks available!', 'error');
        return;
    }

    const attackPanel = document.getElementById('attack-panel');
    const attackOptions = document.getElementById('attack-options');
    attackOptions.innerHTML = '';

    validActions.attack.forEach((attack) => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        const otherPlayerName = gameState.currentPlayer === gameState.player1.name
            ? gameState.player2.name
            : gameState.player1.name;
        button.innerHTML = `
            Attack ${otherPlayerName}'s <strong>${attack.target}</strong> hand 
            with your <strong>${attack.source}</strong> hand (${attack.sourceSticks} sticks)
        `;
        button.addEventListener('click', () => executeAttackFromPanel(attack.source, attack.target));
        attackOptions.appendChild(button);
    });

    hideActionPanels();
    attackPanel.style.display = 'block';
}

async function executeAttackFromPanel(sourceHand, targetHand) {
    try {
        const response = await fetch(`${API_BASE}/game/${gameId}/attack`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sourceHand: sourceHand,
                targetHand: targetHand
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || 'Attack failed!', 'error');
            return;
        }

        gameState = data.gameState;
        validActions = data.validActions;

        const otherPlayerName = gameState.currentPlayer === gameState.player1.name
            ? gameState.player2.name
            : gameState.player1.name;
        showMessage(`Attacked ${otherPlayerName}'s ${targetHand} hand!`, 'success');
        updateGameDisplay();

        if (gameState.gameOver) {
            hideActionPanels();
            showGameOverModal();
        } else {
            hideActionPanels();
            showMessage(`${gameState.currentPlayer}'s turn!`, 'info');
        }
    } catch (error) {
        console.error('Error executing attack:', error);
        showMessage('Failed to execute attack', 'error');
    }
}

function showRedistributePanel() {
    if (!validActions || validActions.redistribute.length === 0) {
        // Shake all hand emoji elements
        const hands = document.querySelectorAll('.hand-emoji');
        hands.forEach(hand => {
            hand.classList.add('shake');
            // Remove the shake class after animation completes so it can be triggered again
            setTimeout(() => hand.classList.remove('shake'), 500);
        });

        showMessage('No valid redistributions available!', 'error');
        return;
    }

    const currentHandLeft = gameState.currentPlayer === gameState.player1.name
        ? gameState.player1.leftHand
        : gameState.player2.leftHand;
    const currentHandRight = gameState.currentPlayer === gameState.player1.name
        ? gameState.player1.rightHand
        : gameState.player2.rightHand;

    const redistributePanel = document.getElementById('redistribute-panel');
    const redistributeOptions = document.getElementById('redistribute-options');
    redistributeOptions.innerHTML = '';

    validActions.redistribute.forEach((redist) => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.innerHTML = `Move from <strong>${redist.from}</strong> to <strong>${redist.to}</strong> (${redist.maxAmount} sticks available)`;
        button.addEventListener('click', () => startRedistribute(redist.from, redist.to, redist.maxAmount));
        redistributeOptions.appendChild(button);
    });

    hideActionPanels();
    redistributePanel.style.display = 'block';
}

function startRedistribute(fromHand, toHand, maxAmount) {
    window.redistributeData = { from: fromHand, to: toHand, max: maxAmount };

    document.getElementById('amount-input').value = 1;
    document.getElementById('amount-input').max = maxAmount;

    hideActionPanels();
    document.getElementById('amount-panel').style.display = 'block';
}

async function confirmAmount() {
    const amount = parseInt(document.getElementById('amount-input').value);
    const data = window.redistributeData;

    if (!data || amount < 1 || amount > data.max) {
        showMessage('Invalid amount!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/game/${gameId}/redistribute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fromHand: data.from,
                toHand: data.to,
                amount: amount
            })
        });

        const result = await response.json();

        if (!response.ok) {
            showMessage(result.error || 'Redistribution failed!', 'error');
            return;
        }

        gameState = result.gameState;
        validActions = result.validActions;

        showMessage(`Redistributed ${amount} stick(s) from ${data.from} to ${data.to}!`, 'success');
        updateGameDisplay();

        if (gameState.gameOver) {
            hideActionPanels();
            showGameOverModal();
        } else {
            hideActionPanels();
            showMessage(`${gameState.currentPlayer}'s turn!`, 'info');
        }
    } catch (error) {
        console.error('Error executing redistribution:', error);
        showMessage('Failed to execute redistribution', 'error');
    }

    window.redistributeData = null;
}

function updateGameDisplay() {
    if (!gameState) return;

    // Update player names
    document.getElementById('player1-name').textContent = gameState.player1.name;
    document.getElementById('player2-name').textContent = gameState.player2.name;

    // Update current player indicator
    document.getElementById('current-player-name').textContent = gameState.currentPlayer;

    // Update hands and fingers
    updateHandDisplay('p1-left', gameState.player1.leftHand);
    updateHandDisplay('p1-right', gameState.player1.rightHand);
    updateHandDisplay('p2-left', gameState.player2.leftHand);
    updateHandDisplay('p2-right', gameState.player2.rightHand);

    // Update stick counts
    document.getElementById('p1-left-count').textContent = gameState.player1.leftHand;
    document.getElementById('p1-right-count').textContent = gameState.player1.rightHand;
    document.getElementById('p2-left-count').textContent = gameState.player2.leftHand;
    document.getElementById('p2-right-count').textContent = gameState.player2.rightHand;

    // Update eliminated status
    updateEliminated('p1-left-hand', gameState.player1.leftHand);
    updateEliminated('p1-right-hand', gameState.player1.rightHand);
    updateEliminated('p2-left-hand', gameState.player2.leftHand);
    updateEliminated('p2-right-hand', gameState.player2.rightHand);

    // Update button disabilities
    updateActionButtons();
}

function updateHandDisplay(handId, stickCount) {
    const imageId = `${handId}-emoji`;
    const imageElement = document.getElementById(imageId);

    if (!imageElement) return;

    // Create image path based on number of sticks
    const imagePath = `images/hand-${stickCount}.png`;
    imageElement.src = imagePath;
}

function updateEliminated(handId, stickCount) {
    const handElement = document.getElementById(handId);
    if (handElement) {
        if (stickCount === 0) {
            handElement.classList.add('eliminated');
        } else {
            handElement.classList.remove('eliminated');
        }
    }
}

function updateActionButtons() {
    const hasAttackOptions = validActions && validActions.attack.length > 0;
    const hasRedistributeOptions = validActions && validActions.redistribute.length > 0;

    document.getElementById('attack-btn').disabled = !hasAttackOptions;
    document.getElementById('redistribute-btn').disabled = !hasRedistributeOptions;
}

function hideActionPanels() {
    document.getElementById('attack-panel').style.display = 'none';
    document.getElementById('redistribute-panel').style.display = 'none';
    document.getElementById('amount-panel').style.display = 'none';
}

function showMessage(text, type = 'info') {
    const messageBox = document.getElementById('message-box');
    messageBox.textContent = text;
    messageBox.className = `message-box ${type}`;

    // Auto-hide after 5 seconds for non-error messages
    if (type !== 'error') {
        setTimeout(() => {
            messageBox.className = 'message-box';
            messageBox.textContent = '';
        }, 5000);
    }
}

function showGameOverModal() {
    const modal = document.getElementById('game-over-modal');
    const message = document.getElementById('winner-message');

    if (gameState.winner) {
        message.textContent = `🎉 ${gameState.winner} wins! 🎉`;
    } else {
        message.textContent = 'Game Over!';
    }

    modal.style.display = 'flex';
}

function resetGame() {
    const setupModal = document.getElementById('setup-modal');
    const gameOverModal = document.getElementById('game-over-modal');

    // Clear inputs but keep previous names if a game has been played
    const currentP1 = gameState ? gameState.player1.name : 'Player 1';
    const currentP2 = gameState ? gameState.player2.name : 'Player 2';

    document.getElementById('player1-input').value = currentP1;
    document.getElementById('player2-input').value = currentP2;

    gameOverModal.style.display = 'none';
    setupModal.style.display = 'flex';
}
