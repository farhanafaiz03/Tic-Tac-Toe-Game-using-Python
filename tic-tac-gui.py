import tkinter as tk
from tkinter import messagebox, simpledialog
from playsound import playsound
import os

# Optional: sound file path (replace with valid paths to .mp3 or .wav)
VICTORY_SOUND = None
DRAW_SOUND = None

class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.score = 0

    def increment_score(self):
        self.score += 1

class Board:
    def __init__(self, gui):
        self.gui = gui
        self.reset()

    def reset(self):
        self.grid = [["" for _ in range(3)] for _ in range(3)]

    def update_cell(self, row, col, symbol):
        if self.grid[row][col] == "":
            self.grid[row][col] = symbol
            return True
        return False

    def is_full(self):
        return all(cell != "" for row in self.grid for cell in row)

    def check_winner(self, symbol):
        g = self.grid
        for i in range(3):
            if all(g[i][j] == symbol for j in range(3)) or all(g[j][i] == symbol for j in range(3)):
                return True
        if g[0][0] == g[1][1] == g[2][2] == symbol or g[0][2] == g[1][1] == g[2][0] == symbol:
            return True
        return False

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe ✨")
        self.root.geometry("400x500")
        self.root.resizable(True, True)
        self.players = []
        self.current_player_index = 0

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(expand=True)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.score_label.pack(pady=5)

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                btn = tk.Button(self.board_frame, text="", font=("Arial", 24), width=4, height=2,
                                command=lambda r=row, c=col: self.play_turn(r, c))
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.buttons[row][col] = btn

        for i in range(3):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

        self.start_new_game()

    def start_new_game(self):
        self.get_player_info()
        self.board = Board(self)
        self.update_ui()
        self.reset_board()

    def get_player_info(self):
        self.players = []
        for i in range(2):
            name = simpledialog.askstring("Player Info", f"Enter name for Player {i + 1}:")
            symbol = simpledialog.askstring("Player Info", f"Enter symbol for {name}:")
            self.players.append(Player(name, symbol))
        self.current_player_index = 0

    def reset_board(self):
        self.board.reset()
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="", state=tk.NORMAL)
        self.update_ui()

    def update_ui(self):
        current = self.players[self.current_player_index]
        self.status_label.config(text=f"{current.name}'s Turn ({current.symbol})")
        score_text = f"{self.players[0].name}: {self.players[0].score} | {self.players[1].name}: {self.players[1].score}"
        self.score_label.config(text=score_text)

    def play_turn(self, row, col):
        current = self.players[self.current_player_index]
        if self.board.update_cell(row, col, current.symbol):
            self.buttons[row][col].config(text=current.symbol)
            if self.board.check_winner(current.symbol):
                current.increment_score()
                self.update_ui()
                if VICTORY_SOUND: playsound(VICTORY_SOUND)
                messagebox.showinfo("Game Over", f"{current.name} wins! 🎉")
                self.ask_replay()
            elif self.board.is_full():
                if DRAW_SOUND: playsound(DRAW_SOUND)
                messagebox.showinfo("Game Over", "It's a draw! 🤝")
                self.ask_replay()
            else:
                self.current_player_index = 1 - self.current_player_index
                self.update_ui()

    def ask_replay(self):
        answer = messagebox.askyesno("Play Again?", "Do you want to play another game?")
        if answer:
            self.reset_board()
        else:
            messagebox.showinfo("Goodbye", "Thanks for playing the game! 🎮")
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
