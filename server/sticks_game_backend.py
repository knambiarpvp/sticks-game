"""
Sticks Game Backend

A Python implementation of the classic Sticks game (also known as Jacks).
Each player has two hands with sticks. Players take turns either attacking
an opponent's hand or redistributing their own sticks.
"""

from typing import Tuple, Optional


class Player:
    """Represents a player in the sticks game."""
    
    def __init__(self, name: str, initial_sticks: int = 1):
        """
        Initialize a player with two hands.
        
        Args:
            name: Player's name
            initial_sticks: Number of sticks each hand starts with (default: 1)
        """
        self.name = name
        self.left_hand = initial_sticks
        self.right_hand = initial_sticks
    
    def get_hands(self) -> Tuple[int, int]:
        """Return a tuple of (left_hand, right_hand) stick counts."""
        return (self.left_hand, self.right_hand)
    
    def get_active_hands(self) -> list:
        """Return list of active hands (non-zero sticks). ['left', 'right', or both]"""
        active = []
        if self.left_hand > 0:
            active.append('left')
        if self.right_hand > 0:
            active.append('right')
        return active
    
    def is_eliminated(self) -> bool:
        """Check if player has no hands remaining (both hands eliminated)."""
        return self.left_hand == 0 and self.right_hand == 0
    
    def has_active_hands(self) -> bool:
        """Check if player has at least one active hand."""
        return self.left_hand > 0 or self.right_hand > 0
    
    def attack(self, source_hand: str, target_player: 'Player', target_hand: str) -> bool:
        """
        Attack an opponent's hand with one of your hands.
        
        Args:
            source_hand: 'left' or 'right' - which hand to attack with
            target_player: The opponent player
            target_hand: 'left' or 'right' - opponent's hand to attack
        
        Returns:
            True if attack was successful, False otherwise
        """
        source_sticks = self.left_hand if source_hand == 'left' else self.right_hand
        
        # Can't attack with an eliminated hand
        if source_sticks == 0:
            return False
        
        # Add attacker's sticks to target hand
        if target_hand == 'left':
            target_player.left_hand += source_sticks
        else:
            target_player.right_hand += source_sticks
        
        # Check if target hand reaches or exceeds maximum (5 sticks) and eliminate if so
        if target_player.left_hand >= 5:
            target_player.left_hand = 0
        if target_player.right_hand >= 5:
            target_player.right_hand = 0
        
        return True
    
    def redistribute(self, from_hand: str, to_hand: str, amount: int) -> bool:
        """
        Move sticks from one hand to another (same player).
        
        Args:
            from_hand: 'left' or 'right' - hand to move from
            to_hand: 'left' or 'right' - hand to move to
            amount: Number of sticks to move
        
        Returns:
            True if redistribution was successful, False otherwise
        """
        if from_hand == to_hand:
            return False
        
        # Get source hand amount
        source_sticks = self.left_hand if from_hand == 'left' else self.right_hand
        
        # Validate amount
        if amount <= 0 or amount > source_sticks:
            return False
        
        # Move sticks from source to target
        if from_hand == 'left':
            self.left_hand -= amount
            self.right_hand += amount
        else:
            self.right_hand -= amount
            self.left_hand += amount
        
        # Check and eliminate hands that exceed 5 sticks
        if self.left_hand > 5:
            self.left_hand = 0
        if self.right_hand > 5:
            self.right_hand = 0
        
        return True
    
    def __str__(self) -> str:
        """Return string representation of player state."""
        left = self.left_hand if self.left_hand > 0 else 'X'
        right = self.right_hand if self.right_hand > 0 else 'X'
        return f"{self.name}: Left={left}, Right={right}"


class Game:
    """Manages the sticks game state and gameplay."""
    
    def __init__(self, player1_name: str, player2_name: str, initial_sticks: int = 1):
        """
        Initialize a new game.
        
        Args:
            player1_name: Name of player 1
            player2_name: Name of player 2
            initial_sticks: Number of sticks each hand starts with (default: 1)
        """
        self.player1 = Player(player1_name, initial_sticks)
        self.player2 = Player(player2_name, initial_sticks)
        self.current_player = self.player1
        self.other_player = self.player2
        self.game_over = False
        self.winner = None
    
    def display_game_state(self) -> None:
        """Display the current game state."""
        print("\n" + "="*50)
        print(self.player1)
        print(self.player2)
        print(f"Current turn: {self.current_player.name}")
        print("="*50 + "\n")
    
    def get_valid_actions(self) -> dict:
        """
        Get all valid actions for the current player.
        
        Returns:
            A dictionary with available actions and targets
        """
        actions = {
            'attack': [],
            'redistribute': []
        }
        
        active_hands = self.current_player.get_active_hands()
        opponent_hands = self.other_player.get_active_hands()
        
        # Possible attacks: each active hand can attack each opponent's active hand
        for source_hand in active_hands:
            for target_hand in opponent_hands:
                actions['attack'].append((source_hand, target_hand))
        
        # Possible redistributions: move from one hand to the other
        if len(active_hands) == 2:
            actions['redistribute'] = [('left', 'right'), ('right', 'left')]
        
        return actions
    
    def execute_attack(self, source_hand: str, target_hand: str) -> bool:
        """
        Execute an attack from the current player to the opponent.
        
        Args:
            source_hand: The current player's hand to use ('left' or 'right')
            target_hand: The opponent's hand to attack ('left' or 'right')
        
        Returns:
            True if attack was successful, False if invalid
        """
        # Validate hands are in valid actions
        valid_actions = self.get_valid_actions()
        if (source_hand, target_hand) not in valid_actions['attack']:
            return False
        
        # Execute the attack
        self.current_player.attack(source_hand, self.other_player, target_hand)
        
        # Check if opponent is eliminated
        if self.other_player.is_eliminated():
            self.end_game()
        else:
            # Swap turns
            self.current_player, self.other_player = self.other_player, self.current_player
        
        return True
    
    def execute_redistribute(self, from_hand: str, to_hand: str, amount: int) -> bool:
        """
        Execute a redistribution action by the current player.
        
        Args:
            from_hand: The hand to move sticks from ('left' or 'right')
            to_hand: The hand to move sticks to ('left' or 'right')
            amount: The number of sticks to move
        
        Returns:
            True if redistribution was successful, False if invalid
        """
        # Validate basic constraints
        if from_hand == to_hand:
            return False  # Can't redistribute to the same hand
        
        if from_hand not in ['left', 'right'] or to_hand not in ['left', 'right']:
            return False  # Invalid hand names
        
        if amount < 1:
            return False  # Must move at least 1 stick
        
        # Execute the redistribution
        if not self.current_player.redistribute(from_hand, to_hand, amount):
            return False
        
        # Check if game is over (shouldn't happen from redistribution, but check anyway)
        if self.other_player.is_eliminated():
            self.end_game()
        else:
            # Swap turns
            self.current_player, self.other_player = self.other_player, self.current_player
        
        return True
    
    def play_turn(self) -> None:
        """
        Execute one player's turn.
        Prompts the current player for their action and validates it.
        """
        self.display_game_state()
        
        valid_actions = self.get_valid_actions()
        
        # Check if player has any valid moves
        if not valid_actions['attack'] and not valid_actions['redistribute']:
            print(f"{self.current_player.name} has no valid moves! Game over.")
            self.end_game()
            return
        
        action_taken = False
        while not action_taken:
            print(f"\n{self.current_player.name}'s turn:")
            print("Actions available:")
            print("1. ATTACK - Hit opponent's hand")
            print("2. REDISTRIBUTE - Move sticks between your hands")
            
            choice = input("\nChoose action (1 for ATTACK, 2 for REDISTRIBUTE): ").strip().lower()
            
            if choice == '1' or choice == 'attack':
                action_taken = self._execute_attack(valid_actions['attack'])
            elif choice == '2' or choice == 'redistribute':
                action_taken = self._execute_redistribute(valid_actions['redistribute'])
            else:
                print("Invalid choice. Please enter 1 or 2.")
        
        # Check if opponent is eliminated
        if self.other_player.is_eliminated():
            self.end_game()
        else:
            # Swap turns
            self.current_player, self.other_player = self.other_player, self.current_player
    
    def _execute_attack(self, valid_attacks: list) -> bool:
        """
        Execute an attack action.
        
        Args:
            valid_attacks: List of valid attack combinations
        
        Returns:
            True if attack was executed, False if invalid input
        """
        if not valid_attacks:
            print("No valid attacks available!")
            return False
        
        print("\nAvailable attacks:")
        for i, (source, target) in enumerate(valid_attacks, 1):
            source_sticks = (self.current_player.left_hand if source == 'left' 
                           else self.current_player.right_hand)
            print(f"{i}. Attack opponent's {target} hand with your {source} hand ({source_sticks} sticks)")
        
        try:
            choice = int(input("\nSelect attack (number): ")) - 1
            if 0 <= choice < len(valid_attacks):
                source_hand, target_hand = valid_attacks[choice]
                self.current_player.attack(source_hand, self.other_player, target_hand)
                print(f"\n{self.current_player.name} attacked {self.other_player.name}'s {target_hand} hand!")
                
                # Announce if opponent's hand was eliminated
                if target_hand == 'left' and self.other_player.left_hand == 0:
                    print(f"{self.other_player.name}'s left hand has been eliminated!")
                elif target_hand == 'right' and self.other_player.right_hand == 0:
                    print(f"{self.other_player.name}'s right hand has been eliminated!")
                
                return True
            else:
                print("Invalid selection.")
                return False
        except ValueError:
            print("Please enter a valid number.")
            return False
    
    def _execute_redistribute(self, valid_redistributes: list) -> bool:
        """
        Execute a redistribute action.
        
        Args:
            valid_redistributes: List of valid redistribute combinations
        
        Returns:
            True if redistribution was executed, False if invalid input
        """
        if not valid_redistributes:
            print("No valid redistributions available!")
            return False
        
        left_sticks = self.current_player.left_hand
        right_sticks = self.current_player.right_hand
        
        # Ask which direction to redistribute
        print("\nAvailable redistributions:")
        if ('left', 'right') in valid_redistributes:
            print(f"1. Move sticks from left hand ({left_sticks}) to right hand")
        if ('right', 'left') in valid_redistributes:
            print(f"2. Move sticks from right hand ({right_sticks}) to left hand")
        
        try:
            direction_choice = int(input("\nSelect direction (1 or 2): "))
            
            if direction_choice == 1 and ('left', 'right') in valid_redistributes:
                # Move from left to right
                amount = self._prompt_for_amount("left", left_sticks)
                if amount is None:
                    return False
                self.current_player.redistribute('left', 'right', amount)
                print(f"\n{self.current_player.name} moved {amount} stick(s) from left to right hand!")
                return True
            elif direction_choice == 2 and ('right', 'left') in valid_redistributes:
                # Move from right to left
                amount = self._prompt_for_amount("right", right_sticks)
                if amount is None:
                    return False
                self.current_player.redistribute('right', 'left', amount)
                print(f"\n{self.current_player.name} moved {amount} stick(s) from right to left hand!")
                return True
            else:
                print("Invalid selection.")
                return False
        except ValueError:
            print("Please enter a valid number.")
            return False
    
    def _prompt_for_amount(self, hand: str, available: int) -> Optional[int]:
        """
        Prompt the player for the number of sticks to move.
        
        Args:
            hand: The hand name ('left' or 'right')
            available: Number of sticks available in that hand
        
        Returns:
            The number of sticks to move, or None if invalid input
        """
        while True:
            try:
                amount = int(input(f"How many sticks to move from {hand} hand (1-{available}): "))
                if 1 <= amount <= available:
                    return amount
                else:
                    print(f"Please enter a number between 1 and {available}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def end_game(self) -> None:
        """End the game and declare the winner."""
        self.game_over = True
        
        if self.other_player.is_eliminated():
            self.winner = self.current_player
            print(f"\n{'='*50}")
            print(f"GAME OVER! {self.winner.name} wins!")
            print(f"{self.other_player.name} has no hands remaining.")
            print(f"{'='*50}\n")
        else:
            print(f"\n{'='*50}")
            print("Game ended - no valid moves available")
            print(f"{'='*50}\n")
    
    def play(self) -> Optional[Player]:
        """
        Run the main game loop until completion.
        
        Returns:
            The winning player, or None if game ended without a winner
        """
        print(f"\nStarting {self.player1.name} vs {self.player2.name}!")
        
        while not self.game_over:
            self.play_turn()
        
        return self.winner


def main():
    """Main function to run a game of sticks."""
    print("Welcome to Sticks Game!")
    print("-" * 50)
    
    player1_name = input("Enter Player 1 name: ").strip() or "Player 1"
    player2_name = input("Enter Player 2 name: ").strip() or "Player 2"
    
    game = Game(player1_name, player2_name, initial_sticks=1)
    winner = game.play()
    
    if winner:
        print(f"Congratulations {winner.name}!")


if __name__ == "__main__":
    main()
