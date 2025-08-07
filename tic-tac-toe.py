from colorama import Fore, Style, init
init(autoreset=True)

class Player:
    def __init__(self, name, symbol, color):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.score = 0

    def colored_symbol(self):
        return self.color + self.symbol + Style.RESET_ALL

class Board:
    def __init__(self):
        self.state = [' ' for _ in range(9)]

    def display(self):
        print("\n")
        for i in range(3):
            row = f" {self.get_cell(i * 3)} | {self.get_cell(i * 3 + 1)} | {self.get_cell(i * 3 + 2)} "
            print(row)
            if i < 2:
                print("---|---|---")
        print("\n")

    def get_cell(self, index):
        return self.state[index] if self.state[index] != ' ' else str(index)

    def make_move(self, index, player):
        if self.state[index] == ' ':
            self.state[index] = player.colored_symbol()
            return True
        return False

    def is_full(self):
        return ' ' not in self.state

    def check_winner(self, player):
        symbol = player.colored_symbol()
        win_combos = [
            [0,1,2],[3,4,5],[6,7,8],  # rows
            [0,3,6],[1,4,7],[2,5,8],  # columns
            [0,4,8],[2,4,6]           # diagonals
        ]
        for combo in win_combos:
            if all(self.state[i] == symbol for i in combo):
                return True
        return False

    def reset(self):
        self.state = [' ' for _ in range(9)]

class Game:
    def __init__(self):
        print(Fore.MAGENTA + "🎮 Welcome to Tic Tac Toe (Terminal Edition) 🎮\n")
        self.player1 = self.create_player("Player 1", Fore.RED)
        self.player2 = self.create_player("Player 2", Fore.BLUE)
        self.board = Board()

    def create_player(self, label, color):
        name = input(f"{label}, enter your name: ")
        symbol = input(f"{name}, choose your symbol (X/O/etc.): ")
        return Player(name, symbol, color)

    def play(self):
        current = self.player1
        while True:
            self.board.display()
            print(f"{current.color}{current.name}'s turn [{current.symbol}]")
            move = self.get_valid_move()

            if self.board.make_move(move, current):
                if self.board.check_winner(current):
                    self.board.display()
                    print(f"🏆 {current.color}{current.name} wins this round!")
                    current.score += 1
                    self.display_scoreboard()
                    if not self.play_again():
                        break
                    self.board.reset()
                    current = self.player1  # reset to first player
                    continue

                if self.board.is_full():
                    self.board.display()
                    print(Fore.YELLOW + "🤝 It's a draw!")
                    if not self.play_again():
                        break
                    self.board.reset()
                    current = self.player1
                    continue

                current = self.switch_player(current)
            else:
                print(Fore.RED + "❌ Invalid move. Try again.")

    def switch_player(self, current):
        return self.player2 if current == self.player1 else self.player1

    def get_valid_move(self):
        while True:
            try:
                move = int(input("Choose a position (0-8): "))
                if move not in range(9):
                    raise ValueError("Must be between 0-8")
                if self.board.state[move] != ' ':
                    raise ValueError("That position is already filled")
                return move
            except ValueError as ve:
                print(Fore.RED + f"⚠️ {ve}")

    def display_scoreboard(self):
        print(Fore.CYAN + "\n📊 Scoreboard:")
        print(f"{self.player1.name}: {self.player1.score}")
        print(f"{self.player2.name}: {self.player2.score}\n")

    def play_again(self):
        again = input("🔁 Play again? (y/n): ").lower()
        return again == 'y'

if __name__ == "__main__":
    game = Game()
    game.play()
