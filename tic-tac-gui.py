import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
import threading
import os

# Try to import playsound. If not present, sound calls will be ignored gracefully.
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except Exception:
    PLAYSOUND_AVAILABLE = False

# ---------- Optional: point these to your sound files (mp3/wav) ----------
# Put sound files in same folder (or give absolute path). If not present, no sound will play.
SOUND_MOVE = "click.mp3"   # short click sound when placing a move
SOUND_WIN = "win.mp3"      # win sound
SOUND_DRAW = "draw.mp3"    # draw sound
# -----------------------------------------------------------------------

# Default emoji/symbols and colors
DEFAULT_X = {"symbol": "❌", "color": "#d64541"}  # red-ish
DEFAULT_O = {"symbol": "⭕", "color": "#2a9df4"}  # blue-ish
BG_BOARD = "#ffffff"
HIGHLIGHT_BG = "#dff0d8"  # greenish highlight for win

class PlayerInfo:
    def __init__(self, name: str, symbol: str, color: str):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.score = 0

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        root.title("Tic-Tac-Toe")
        root.configure(bg=BG_BOARD)
        # make window resizable & responsive
        root.geometry("520x640")
        root.minsize(420, 520)
        root.rowconfigure(2, weight=1)
        root.columnconfigure(0, weight=1)

        # Title (centered)
        title_font = tkfont.Font(family="Helvetica", size=22, weight="bold", slant="italic")
        self.title_label = tk.Label(root, text="Tic-Tac-Toe", font=title_font, bg=BG_BOARD)
        self.title_label.grid(row=0, column=0, pady=(12,6), sticky="n")

        # Top panel frame: boxed area containing input fields and scoreboard
        self.top_frame = tk.Frame(root, bg="#f8f9fa", bd=2, relief="solid", padx=12, pady=12)
        self.top_frame.grid(row=1, column=0, padx=20, sticky="ew")
        self.top_frame.columnconfigure((0,1,2,3), weight=1)

        self._build_top_panel()

        # Game board frame (below the top box)
        self.board_frame = tk.Frame(root, bg=BG_BOARD)
        self.board_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=16)
        self.board_frame.rowconfigure((0,1,2), weight=1)
        self.board_frame.columnconfigure((0,1,2), weight=1)

        self._build_board()

        # Bottom controls
        ctrl_frame = tk.Frame(root, bg=BG_BOARD)
        ctrl_frame.grid(row=3, column=0, pady=(0,12))
        self.play_again_btn = tk.Button(ctrl_frame, text="Play Again (keep scores)", command=self.play_again)
        self.play_again_btn.grid(row=0, column=0, padx=8)
        self.reset_scores_btn = tk.Button(ctrl_frame, text="Reset Scores", command=self.reset_scores)
        self.reset_scores_btn.grid(row=0, column=1, padx=8)
        self.quit_btn = tk.Button(ctrl_frame, text="Exit", command=self._exit_app)
        self.quit_btn.grid(row=0, column=2, padx=8)

        # Initialize game state
        self.reset_game(initial_setup=True)

    # ------------------ Top panel (inputs + scoreboard) ------------------
    def _build_top_panel(self):
        lbl_font = tkfont.Font(size=10, weight="bold")
        small_font = tkfont.Font(size=10)

        # Player 1 labels & entries (left)
        p1_label = tk.Label(self.top_frame, text="Player 1", font=lbl_font, bg="#f8f9fa")
        p1_label.grid(row=0, column=0, sticky="w")
        self.p1_name_var = tk.StringVar(value="Player X")
        self.p1_name_entry = tk.Entry(self.top_frame, textvariable=self.p1_name_var, font=small_font)
        self.p1_name_entry.grid(row=1, column=0, sticky="ew", padx=(0,8))

        p1_sym_label = tk.Label(self.top_frame, text="Symbol", font=lbl_font, bg="#f8f9fa")
        p1_sym_label.grid(row=0, column=1, sticky="w")
        self.p1_sym_var = tk.StringVar(value=DEFAULT_X["symbol"])
        self.p1_sym_entry = tk.Entry(self.top_frame, textvariable=self.p1_sym_var, width=4, font=small_font, justify="center")
        self.p1_sym_entry.grid(row=1, column=1, sticky="w")

        # Player 2 labels & entries (right)
        p2_label = tk.Label(self.top_frame, text="Player 2", font=lbl_font, bg="#f8f9fa")
        p2_label.grid(row=0, column=2, sticky="w", padx=(10,0))
        self.p2_name_var = tk.StringVar(value="Player O")
        self.p2_name_entry = tk.Entry(self.top_frame, textvariable=self.p2_name_var, font=small_font)
        self.p2_name_entry.grid(row=1, column=2, sticky="ew", padx=(10,8))

        p2_sym_label = tk.Label(self.top_frame, text="Symbol", font=lbl_font, bg="#f8f9fa")
        p2_sym_label.grid(row=0, column=3, sticky="w")
        self.p2_sym_var = tk.StringVar(value=DEFAULT_O["symbol"])
        self.p2_sym_entry = tk.Entry(self.top_frame, textvariable=self.p2_sym_var, width=4, font=small_font, justify="center")
        self.p2_sym_entry.grid(row=1, column=3, sticky="w")

        # Scoreboard row (below inputs)
        self.scoreboard_label = tk.Label(self.top_frame, text="", font=tkfont.Font(size=11), bg="#f8f9fa")
        self.scoreboard_label.grid(row=2, column=0, columnspan=4, pady=(12,0))

        # Apply button to commit names/symbols
        apply_btn = tk.Button(self.top_frame, text="Set Players", command=self.apply_player_settings)
        apply_btn.grid(row=3, column=0, columnspan=4, pady=(10,0))

    def apply_player_settings(self):
        # Validate entries and update the PlayerInfo objects
        p1_name = (self.p1_name_var.get() or "Player X").strip()
        p2_name = (self.p2_name_var.get() or "Player O").strip()
        p1_sym = (self.p1_sym_var.get() or DEFAULT_X["symbol"]).strip()
        p2_sym = (self.p2_sym_var.get() or DEFAULT_O["symbol"]).strip()

        if p1_name == p2_name:
            messagebox.showwarning("Names conflict", "Please choose different names for players.")
            return
        if p1_sym == p2_sym:
            messagebox.showwarning("Symbols conflict", "Please choose different symbols for players.")
            return
        # Keep sensible single-char fallback (emoji allowed)
        if len(p1_sym) > 2: p1_sym = p1_sym[0]
        if len(p2_sym) > 2: p2_sym = p2_sym[0]

        # Colors remain defaults but could be extended with color pickers
        self.player1 = PlayerInfo(p1_name, p1_sym, DEFAULT_X["color"])
        self.player2 = PlayerInfo(p2_name, p2_sym, DEFAULT_O["color"])
        # Ensure score keys exist if first time
        if not hasattr(self, "scores"):
            self.scores = {self.player1.name: 0, self.player2.name: 0, "Draws": 0}
        else:
            # If names changed, preserve old scores when possible
            prev = dict(self.scores)
            self.scores = {self.player1.name: prev.get(self.player1.name, 0),
                           self.player2.name: prev.get(self.player2.name, 0),
                           "Draws": prev.get("Draws", 0)}
        self.update_scoreboard()
        # reset board to start fresh after changing players
        self.reset_board_state()

    def update_scoreboard(self):
        if not hasattr(self, "scores"):
            self.scores = { "Player X": 0, "Player O": 0, "Draws": 0 }
        # Build scoreboard text neatly
        p1_name = getattr(self, "player1", None).name if getattr(self, "player1", None) else "Player X"
        p2_name = getattr(self, "player2", None).name if getattr(self, "player2", None) else "Player O"
        scoreboard_text = f"{p1_name}: {self.scores.get(p1_name,0)}    |    {p2_name}: {self.scores.get(p2_name,0)}    |    Draws: {self.scores.get('Draws',0)}"
        self.scoreboard_label.config(text=scoreboard_text)

    # ------------------ Build 3x3 board ------------------
    def _build_board(self):
        self.cell_buttons = {}
        btn_font = tkfont.Font(size=40, weight="bold")  # big emoji/symbol
        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.board_frame, text="", font=btn_font, bd=2, relief="ridge",
                                command=lambda rr=r, cc=c: self.on_cell_click(rr, cc))
                btn.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
                # attach hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#f0f8ff"))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self._default_cell_bg()))
                self.cell_buttons[(r,c)] = btn

    def _default_cell_bg(self):
        return "SystemButtonFace"

    # ------------------ Game logic ------------------
    def reset_game(self, initial_setup=False):
        # Setup default players if not set
        if not hasattr(self, "player1"):
            self.player1 = PlayerInfo("Player X", DEFAULT_X["symbol"], DEFAULT_X["color"])
        if not hasattr(self, "player2"):
            self.player2 = PlayerInfo("Player O", DEFAULT_O["symbol"], DEFAULT_O["color"])
        # scores dictionary
        if not hasattr(self, "scores"):
            self.scores = {self.player1.name: 0, self.player2.name: 0, "Draws": 0}

        self.current = self.player1
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        self.winner_line = None
        self.moves = 0
        if not initial_setup:
            self.update_scoreboard()
        # apply UI fields
        self.p1_name_var.set(self.player1.name)
        self.p2_name_var.set(self.player2.name)
        self.p1_sym_var.set(self.player1.symbol)
        self.p2_sym_var.set(self.player2.symbol)
        self.reset_board_ui()

    def reset_board_ui(self):
        for (r,c), btn in self.cell_buttons.items():
            btn.config(text="", state="normal", fg="#000", bg=self._default_cell_bg())

    def reset_board_state(self):
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        self.moves = 0
        self.winner_line = None
        self.current = self.player1
        self.reset_board_ui()

    def on_cell_click(self, r, c):
        if self.board_state[r][c] != "":
            return
        # Place symbol
        self.board_state[r][c] = self.current.symbol
        btn = self.cell_buttons[(r,c)]
        btn.config(text=self.current.symbol, fg=self.current.color, state="disabled", bg=self._default_cell_bg())
        self.moves += 1
        # Play move sound asynchronously
        self._play_sound("move")
        # Check for win
        winner_line = self._check_winner(self.current.symbol)
        if winner_line:
            # highlight winner line
            self.winner_line = winner_line
            self._highlight_line(winner_line)
            # update score
            self.scores[self.current.name] = self.scores.get(self.current.name, 0) + 1
            self.update_scoreboard()
            # show message
            messagebox.showinfo("We have a winner!", f"{self.current.name} wins! 🎉")
            self._play_sound("win")
            # disable all cells
            self._disable_all_cells()
        elif self.moves == 9:
            self.scores["Draws"] = self.scores.get("Draws", 0) + 1
            self.update_scoreboard()
            messagebox.showinfo("Draw", "It's a draw! 🤝")
            self._play_sound("draw")
        else:
            # switch player
            self.current = self.player2 if self.current == self.player1 else self.player1

    def _disable_all_cells(self):
        for btn in self.cell_buttons.values():
            btn.config(state="disabled")

    def _highlight_line(self, line_coords):
        for (r,c) in line_coords:
            btn = self.cell_buttons[(r,c)]
            btn.config(bg=HIGHLIGHT_BG)

    def _check_winner(self, symbol):
        b = self.board_state
        # rows
        for r in range(3):
            if b[r][0] == b[r][1] == b[r][2] == symbol:
                return [(r,0),(r,1),(r,2)]
        # cols
        for c in range(3):
            if b[0][c] == b[1][c] == b[2][c] == symbol:
                return [(0,c),(1,c),(2,c)]
        # diag
        if b[0][0] == b[1][1] == b[2][2] == symbol:
            return [(0,0),(1,1),(2,2)]
        if b[0][2] == b[1][1] == b[2][0] == symbol:
            return [(0,2),(1,1),(2,0)]
        return None

    def play_again(self):
        # Keep scores; reset board
        self.reset_board_state()

    def reset_scores(self):
        # clear scoreboard and reset counts
        if messagebox.askyesno("Reset Scores", "Reset all scores (including draws)?"):
            self.scores = {self.player1.name: 0, self.player2.name: 0, "Draws": 0}
            self.update_scoreboard()
            self.reset_board_state()

    def _exit_app(self):
        messagebox.showinfo("Thanks!", "Thanks for playing the game! 🎮 Stay awesome ✨")
        self.root.quit()

    # ------------------ Sound handling ------------------
    def _play_sound(self, kind: str):
        # kind: "move", "win", "draw"
        # playsound can block; run it on a thread. If file missing or playsound not installed -> ignore silently.
        if not PLAYSOUND_AVAILABLE:
            return
        sound_file = None
        if kind == "move":
            sound_file = SOUND_MOVE
        elif kind == "win":
            sound_file = SOUND_WIN
        elif kind == "draw":
            sound_file = SOUND_DRAW
        # only play if file exists
        if sound_file and os.path.isfile(sound_file):
            threading.Thread(target=lambda: playsound(sound_file), daemon=True).start()

# ------------------ Run the application ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
