"""
Test and demonstration of the Sticks Game Backend

This file demonstrates how to use the sticks_game_backend module
and includes some basic test cases.
"""

from sticks_game_backend import Player, Game


def test_player_class():
    """Test the Player class functionality."""
    print("Testing Player class...")
    print("-" * 50)
    
    player = Player("Alice", initial_sticks=1)
    print(f"Player created: {player}")
    print(f"Active hands: {player.get_active_hands()}")
    print(f"Is eliminated: {player.is_eliminated()}")
    
    # Test elimination
    player.left_hand = 0
    player.right_hand = 0
    print(f"After elimination: {player}")
    print(f"Is eliminated: {player.is_eliminated()}")
    print()


def test_attack():
    """Test the attack mechanic."""
    print("Testing attack mechanic...")
    print("-" * 50)
    
    attacker = Player("Alice", initial_sticks=2)
    defender = Player("Bob", initial_sticks=1)
    
    print(f"Before attack:")
    print(f"  {attacker}")
    print(f"  {defender}")
    
    # Alice attacks Bob's left hand with her left hand (2 sticks)
    attacker.attack('left', defender, 'left')
    
    print(f"\nAfter Alice attacks Bob's left hand with her left hand:")
    print(f"  {attacker}")
    print(f"  {defender}")
    
    # Bob's left hand should now have 1 + 2 = 3 sticks
    assert defender.left_hand == 3, "Attack result incorrect"
    print("✓ Attack mechanic works correctly")
    print()


def test_redistribution():
    """Test the redistribution mechanic."""
    print("Testing redistribution mechanic...")
    print("-" * 50)
    
    # Test moving partial amount
    player = Player("Alice", initial_sticks=2)
    print(f"Before redistribution: {player}")
    
    player.redistribute('left', 'right', 1)
    print(f"After moving 1 stick from left to right: {player}")
    
    assert player.left_hand == 1, "Left hand should be 1"
    assert player.right_hand == 3, "Right hand should be 3"
    
    # Test moving all remaining sticks
    player.redistribute('left', 'right', 1)
    print(f"After moving remaining 1 stick from left to right: {player}")
    
    assert player.left_hand == 0, "Left hand should be 0"
    assert player.right_hand == 4, "Right hand should be 4"
    print("✓ Redistribution works correctly with partial amounts")
    print()


def test_elimination_by_overflow():
    """Test that hands with more than 5 sticks are eliminated."""
    print("Testing elimination by overflow...")
    print("-" * 50)
    
    attacker = Player("Alice", initial_sticks=3)
    defender = Player("Bob", initial_sticks=3)
    
    print(f"Before attack: {defender}")
    
    # Attack with 3 sticks onto 3 sticks = 6, which should eliminate the hand
    attacker.attack('left', defender, 'left')
    
    print(f"After attack: {defender}")
    print(f"Left hand (should be 0): {defender.left_hand}")
    
    assert defender.left_hand == 0, "Hand with 6 sticks should be eliminated"
    print("✓ Overflow elimination works correctly")
    print()


def test_game_initialization():
    """Test game initialization and state."""
    print("Testing Game initialization...")
    print("-" * 50)
    
    game = Game("Player 1", "Player 2", initial_sticks=1)
    
    print(f"Game created with:")
    print(f"  {game.player1}")
    print(f"  {game.player2}")
    print(f"  Current player: {game.current_player.name}")
    print(f"  Game over: {game.game_over}")
    
    assert game.current_player == game.player1, "Player 1 should start"
    assert game.game_over == False, "Game should not be over"
    print("✓ Game initialization works correctly")
    print()


def test_valid_actions():
    """Test valid actions detection."""
    print("Testing valid actions detection...")
    print("-" * 50)
    
    game = Game("Alice", "Bob", initial_sticks=1)
    actions = game.get_valid_actions()
    
    print(f"Valid attacks: {actions['attack']}")
    print(f"Valid redistributions: {actions['redistribute']}")
    
    # With 1 stick in each hand, should have 2 attacks (left->left, left->right, right->left, right->right)
    # and 2 redistributions
    assert len(actions['attack']) > 0, "Should have attack options"
    assert len(actions['redistribute']) == 2, "Should have 2 redistribution options"
    print("✓ Valid actions detection works correctly")
    print()


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("RUNNING STICKS GAME BACKEND TESTS")
    print("=" * 50 + "\n")
    
    test_player_class()
    test_attack()
    test_redistribution()
    test_elimination_by_overflow()
    test_game_initialization()
    test_valid_actions()
    
    print("=" * 50)
    print("ALL TESTS PASSED ✓")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all_tests()
