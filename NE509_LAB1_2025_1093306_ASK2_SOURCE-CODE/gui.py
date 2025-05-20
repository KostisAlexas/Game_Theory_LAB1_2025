# gui.py
import tkinter as tk
from tkinter import messagebox, font
import random
from computer_strategy import get_random_move

# Διάσταση κάθε τετραγώνου και μέγεθος σκακιέρας
SQUARE_SIZE = 80  # Μεγαλύτερο μέγεθος για καλύτερη εμφάνιση
BOARD_SIZE = 8
COLOR_WHITE = "#ffffff"
COLOR_GRAY = "#808180"
COLOR_HIGHLIGHT = "#ffff00"  # Έντονο highlight (κίτρινο για αντίθεση)
BORDER_WIDTH = 4  # Πάχος του περιγράμματος

# Συντεταγμένες στήλης και γραμμής
COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8']


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Δούρειος Ιππος")
        canvas_width = SQUARE_SIZE * BOARD_SIZE + 50
        canvas_height = SQUARE_SIZE * BOARD_SIZE + 50
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        # Μεγαλύτερο TextBox που καταλαμβάνει όλο το πλάτος κάτω από τη σκακιέρα, μη επεξεργάσιμο και με μπλε κείμενο
        self.textbox = tk.Text(root, height=10, width=canvas_width // 10, fg="blue", state="disabled")
        self.textbox.grid(row=2, column=0, columnspan=4, padx=10, pady=10)
        # Επαναδιαμόρφωση των επιλογών: πρώτα το setup της σκακιέρας, μετά το αν παίζει πρώτος
        self.setup_choice = tk.StringVar(value="Ναι")
        self.first_choice = tk.StringVar(value="Ναι")
        tk.Label(root, text="Θέλετε να γίνει setup της σκακιέρας από το σύστημα;").grid(row=1, column=0, columnspan=2,
                                                                                        sticky="w")
        tk.Radiobutton(root, text="Ναι", variable=self.setup_choice, value="Ναι").grid(row=1, column=2, sticky="w")
        tk.Radiobutton(root, text="Όχι", variable=self.setup_choice, value="Όχι").grid(row=1, column=3, sticky="w")
        tk.Label(root, text="Θέλετε να παίξετε πρώτος ως πράσινος;").grid(row=1, column=4, sticky="w")
        tk.Radiobutton(root, text="Ναι", variable=self.first_choice, value="Ναι").grid(row=1, column=5, sticky="w")
        tk.Radiobutton(root, text="Όχι", variable=self.first_choice, value="Όχι").grid(row=1, column=6, sticky="w")
        self.start_button = tk.Button(root, text="Έναρξη παιχνιδιού", command=self.start_or_clear)
        self.start_button.grid(row=3, column=0, columnspan=3, pady=10)
        self.restart_button = tk.Button(root, text="Νέο παιχνίδι", command=self.restart_game, state="disabled")
        self.restart_button.grid(row=3, column=3, columnspan=3, pady=10)

        self.knight = None  # τρέχουσα θέση ως (col_index, row_index)
        self.turn = None  # "πράσινος" ή "κόκκινος"
        self.allowed_moves = []
        self.knight_text_id = None
        self.game_started = False

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def draw_board(self):
        self.canvas.delete("all")
        offset = 30  # για τους αριθμούς/γράμματα
        # Στήλες πάνω
        for i, col in enumerate(COLUMNS):
            self.canvas.create_text(offset + i * SQUARE_SIZE + SQUARE_SIZE / 2, offset / 2, text=col,
                                    font=("Arial", 16, "bold"))
        # Γραμμές αριστερά
        for i, row in enumerate(ROWS):
            self.canvas.create_text(offset / 2, offset + i * SQUARE_SIZE + SQUARE_SIZE / 2, text=row,
                                    font=("Arial", 16, "bold"))
        # Σχεδίαση τετραγώνων
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = offset + c * SQUARE_SIZE
                y1 = offset + r * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = COLOR_WHITE if (r + c) % 2 == 0 else COLOR_GRAY
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1,
                                             tags=f"square_{c}_{r}")
        # Έξωτερικό περίγραμμα γύρω από ολόκληρη τη σκακιέρα για ομορφιά
        board_left = offset
        board_top = offset
        board_right = offset + BOARD_SIZE * SQUARE_SIZE
        board_bottom = offset + BOARD_SIZE * SQUARE_SIZE
        self.canvas.create_rectangle(board_left, board_top, board_right, board_bottom, outline="black",
                                     width=BORDER_WIDTH)

    def start_or_clear(self):
        # Αν το παιχνίδι έχει ήδη ξεκινήσει, το κουμπί μετατρέπεται σε "Εκαθάριση"
        if self.game_started:
            self.clear_board()
        else:
            self.start_game()

    def start_game(self):
        self.clear_board()
        self.game_started = True
        self.restart_button.config(state="disabled")
        self.knight = None
        # Ορισμός πρώτου παίκτη βάσει επιλογής χρήστη
        if self.first_choice.get() == "Ναι":
            self.turn = "πράσινος"
        else:
            self.turn = "κόκκινος"
        self.log(f"Ξεκινά ο {self.turn}.")
        # Τοποθέτηση ίππου: setup από το σύστημα ή ο χρήστης επιλέγει
        if self.setup_choice.get() == "Όχι":
            # Τοποθέτηση τυχαία
            col = random.randint(0, BOARD_SIZE - 1)
            row = random.randint(0, BOARD_SIZE - 1)
            self.knight = (col, row)
            self.log(f"Ο ίππος τοποθετήθηκε τυχαία στη θέση {COLUMNS[col]}{ROWS[row]}.")
            self.draw_knight()
            self.highlight_moves()
            if self.turn == "κόκκινος":
                self.root.after(1000, self.computer_move)
        else:
            self.log("Παρακαλώ επιλέξτε τετράγωνο για τοποθέτηση του ίππου.")

    def clear_board(self):
        self.draw_board()
        self.textbox.config(state="normal")
        self.textbox.delete("1.0", tk.END)
        self.textbox.config(state="disabled")
        self.knight = None
        self.allowed_moves = []
        self.game_started = False
        self.start_button.config(text="Έναρξη παιχνιδιού")
        self.restart_button.config(state="disabled")

    def restart_game(self):
        self.start_button.config(state="normal", text="Έναρξη παιχνιδιού")
        self.restart_button.config(state="disabled")
        self.clear_board()

    def on_canvas_click(self, event):
        offset = 30
        if event.x < offset or event.y < offset:
            return
        col = (event.x - offset) // SQUARE_SIZE
        row = (event.y - offset) // SQUARE_SIZE
        if col < 0 or col >= BOARD_SIZE or row < 0 or row >= BOARD_SIZE:
            return

        # Αν ο χρήστης πρέπει να τοποθετήσει τον ίππο
        if self.knight is None and self.setup_choice.get() == "Ναι":
            self.knight = (col, row)
            self.log(f"Ο ίππος τοποθετήθηκε στη θέση {COLUMNS[col]}{ROWS[row]}.")
            self.draw_knight()
            self.highlight_moves()
            if self.turn == "κόκκινος":
                self.root.after(1000, self.computer_move)
            return

        # Αν ο ίππος υπάρχει και είναι σειρά του χρήστη
        if self.turn == "πράσινος":
            if (col, row) in self.allowed_moves:
                self.move_knight((col, row))
                self.turn = "κόκκινος"
                self.log(f"Ο χρήστης μετακίνησε τον ίππο στη θέση {COLUMNS[col]}{ROWS[row]}.")
                self.clear_highlights()
                self.draw_knight()
                self.root.after(1000, self.computer_move)
            else:
                self.log("Μη επιτρεπτή κίνηση. Επιλέξτε ένα από τα highlighted τετράγωνα.")

    def move_knight(self, new_pos):
        self.knight = new_pos
        self.draw_board()
        self.draw_knight()
        self.highlight_moves()

    def draw_knight(self):
        self.canvas.delete("knight")
        if self.knight is None:
            return
        col, row = self.knight
        offset = 30
        x = offset + col * SQUARE_SIZE + SQUARE_SIZE / 2
        y = offset + row * SQUARE_SIZE + SQUARE_SIZE / 2
        color = "green" if self.turn == "πράσινος" else "red"
        f = font.Font(size=24, weight="bold")
        self.knight_text_id = self.canvas.create_text(x, y, text="Η", fill=color, font=f, tags="knight")

    def highlight_moves(self):
        self.clear_highlights()
        if self.knight is None:
            self.allowed_moves = []
            return
        col, row = self.knight
        moves = []
        possible = [(col - 2, row - 1), (col - 1, row - 2)]
        for pos in possible:
            c, r = pos
            if 0 <= c < BOARD_SIZE and 0 <= r < BOARD_SIZE:
                moves.append(pos)
        self.allowed_moves = [m for m in moves if m[0] < col and m[1] < row]
        offset = 30
        for pos in self.allowed_moves:
            c, r = pos
            x1 = offset + c * SQUARE_SIZE
            y1 = offset + r * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLOR_HIGHLIGHT, stipple="", tags="highlight")

    def clear_highlights(self):
        self.canvas.delete("highlight")

    def computer_move(self):
        if self.turn != "κόκκινος":
            return
        if self.knight is None:
            return
        new_pos = get_random_move(self.knight)
        if new_pos is None:
            self.log("Ο υπολογιστής δεν έχει επιτρεπτές κινήσεις. Νικησάτε!")
            self.end_game()
            return
        self.move_knight(new_pos)
        self.log(f"Ο υπολογιστής μετακίνησε τον ίππο στη θέση {COLUMNS[new_pos[0]]}{ROWS[new_pos[1]]}.")
        if not self.allowed_moves:
            self.log("Δεν έχετε διαθέσιμες κινήσεις. Ο υπολογιστής κερδίζει!")
            self.end_game()
            return
        self.turn = "πράσινος"

    def log(self, message):
        self.textbox.config(state="normal")
        self.textbox.insert(tk.END, message + "\n")
        self.textbox.see(tk.END)
        self.textbox.config(state="disabled")

    def end_game(self):
        self.restart_button.config(state="normal")
        self.start_button.config(state="normal", text="Εκαθάριση")


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
