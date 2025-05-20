# gui.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from computer_strategy import best_computer_move  # strategic move for computer


# Βοηθητική συνάρτηση για τον υπολογισμό των έγκυρων κινήσεων σε μια στήλη
def compute_valid_moves(col, current_row, board_dict):
    moves = []
    # Έλεγχος προς τα πάνω
    row = current_row - 1
    while row >= 1:
        if (board_dict["GREEN"].get(col, None) == row) or (board_dict["RED"].get(col, None) == row):
            break
        moves.append(row)
        row -= 1
    # Έλεγχος προς τα κάτω
    row = current_row + 1
    while row <= 8:
        if (board_dict["GREEN"].get(col, None) == row) or (board_dict["RED"].get(col, None) == row):
            break
        moves.append(row)
        row += 1
    return moves


def auto_board_setup():
    board_dict = {"GREEN": {}, "RED": {}}
    for col in 'abcdefgh':
        rows = random.sample(range(1, 9), 2)
        board_dict["GREEN"][col] = rows[0]
        board_dict["RED"][col] = rows[1]
    return board_dict


class GameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Πύργοι και Σκακιέρα")
        self.master.geometry("1000x800")

        # Frame για τις ρυθμίσεις στο πάνω μέρος
        self.settings_frame = tk.Frame(master, bg="#ddeeff", padx=10, pady=10)
        self.settings_frame.pack(fill=tk.X, padx=20, pady=10)

        # Ρυθμίσεις: Auto board setup
        self.auto_var = tk.StringVar(value="n")
        tk.Label(self.settings_frame, text="Να συμπληρωθεί αυτόματα η σκακιέρα;", font=("Helvetica", 12, "bold"),
                 bg="#ddeeff").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(self.settings_frame, text="Ναι", variable=self.auto_var, value="y", font=("Helvetica", 12),
                       bg="#ddeeff").grid(row=0, column=1, padx=10)
        tk.Radiobutton(self.settings_frame, text="Όχι", variable=self.auto_var, value="n", font=("Helvetica", 12),
                       bg="#ddeeff").grid(row=0, column=2, padx=10)

        # Ρυθμίσεις: Επιλογή πρώτου παιχτή
        self.first_var = tk.StringVar(value="y")
        tk.Label(self.settings_frame, text="Θέλετε να παίξεται πρώτοι ως πράσινος;", font=("Helvetica", 12, "bold"),
                 bg="#ddeeff").grid(row=1, column=0, sticky="w")
        tk.Radiobutton(self.settings_frame, text="Ναι", variable=self.first_var, value="y", font=("Helvetica", 12),
                       bg="#ddeeff").grid(row=1, column=1, padx=10)
        tk.Radiobutton(self.settings_frame, text="Όχι", variable=self.first_var, value="n", font=("Helvetica", 12),
                       bg="#ddeeff").grid(row=1, column=2, padx=10)

        # Κουμπί έναρξης παιχνιδιού
        self.start_btn = tk.Button(self.settings_frame, text="Έναρξη Παιχνιδιού", font=("Helvetica", 12, "bold"),
                                   command=self.start_game)
        self.start_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Frame για το board
        self.board_frame = tk.Frame(master, bg="#e0e0e0")
        self.board_frame.pack(padx=20, pady=10)

        # Textbox μηνυμάτων συστήματος (με μεγαλύτερο μέγεθος και διάστιχο)
        self.message_box = scrolledtext.ScrolledText(master, width=100, height=20, state='disabled',
                                                     bg="#f8f8ff", fg="blue", font=("Helvetica", 12))
        self.message_box.pack(padx=20, pady=10)

        # Κουμπί για Νέο Παιχνίδι (αρχικά κρυφό)
        self.new_game_btn = tk.Button(master, text="Νέο Παιχνίδι", font=("Helvetica", 14, "bold"),
                                      command=self.reset_game)
        self.new_game_btn.pack(pady=10)
        self.new_game_btn.pack_forget()

        self.footer_label = tk.Label(master, text="Developed by Konstantinos Alexopoulos 1093306 ©", font=("Helvetica", 10, "italic"), fg="gray")
        self.footer_label.pack(side="bottom", pady=5)

        # Δημιουργία 8x8 grid κουμπιών για το board
        self.buttons = {}
        for r in range(8):
            for c in range(8):
                btn = tk.Button(self.board_frame, text=" ", width=6, height=3, font=("Helvetica", 14, "bold"),
                                command=lambda r=r, c=c: self.cell_clicked(r, c))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[(r, c)] = btn

        # Εμφάνιση ετικετών στηλών (a-h) και γραμμών (1-8)
        for c, letter in enumerate('abcdefgh'):
            lbl = tk.Label(self.board_frame, text=letter, font=("Helvetica", 14, "bold"), bg="#e0e0e0")
            lbl.grid(row=0, column=c, sticky="n", padx=2, pady=2)
        for r in range(8):
            lbl = tk.Label(self.board_frame, text=str(r + 1), font=("Helvetica", 14, "bold"), bg="#e0e0e0")
            lbl.grid(row=r, column=0, sticky="w", padx=2, pady=2)

        self.footer_label = tk.Label(master, text="Developed by Konstantinos Alexopoulos 1093306 ©", font=("Helvetica", 10, "italic"), fg="gray")
        self.footer_label.pack(side="bottom", pady=5)

        # Καθορισμός αρχικών μεταβλητών
        self.mode = None  # "setup_green", "setup_red", "game"
        self.board_dict = {"GREEN": {}, "RED": {}}
        self.human_player = None
        self.computer_player = None

        # Μεταβλητή για αποθήκευση της επιλεγμένης στήλης (δεν απαιτείται επιλογή πύργου)
        self.selected_col = None

    def start_game(self):
        # Ανάγνωση επιλογών από το settings_frame
        auto_choice = self.auto_var.get().strip().lower()
        first_choice = self.first_var.get().strip().lower()
        if auto_choice == "y":
            self.board_dict = auto_board_setup()
            self.print_message("Το board συμπληρώθηκε αυτόματα.")
            self.mode = "game"
        else:
            self.mode = "setup_green"
            self.print_message("Τοποθετήστε τους Πράσινους πύργους κάνοντας κλικ στα κενά κελιά (ένας πύργος ανά στήλη).")
        if first_choice == "y":
            self.human_player = "GREEN"
            self.computer_player = "RED"
            self.print_message("Θα παίξετε πρώτος ως Πράσινος.")
        else:
            self.human_player = "RED"
            self.computer_player = "GREEN"
            self.print_message("Θα παίξετε δεύτερος ως Κόκκινος. Ο υπολογιστής παίζει πρώτος ως Πράσινος.")
        # Αποκρύπτουμε το settings_frame ώστε να μην ενοχλεί το gameplay
        self.settings_frame.pack_forget()
        self.update_board_gui()
        # Αν ο υπολογιστής παίζει πρώτος, ξεκινάμε κίνηση του
        if self.mode == "game" and self.human_player == "RED":
            self.master.after(1000, self.computer_move)

    def print_message(self, msg):
        self.message_box.configure(state='normal')
        self.message_box.insert(tk.END, msg + "\n\n")
        self.message_box.see(tk.END)
        self.message_box.configure(state='disabled')

    def update_board_gui(self):
        # Ενημέρωση εμφάνισης για κάθε κελί του board σύμφωνα με τις θέσεις στο board_dict
        for (r, c), btn in self.buttons.items():
            btn.config(text=" ", bg="white")
        for col, row in self.board_dict["GREEN"].items():
            r, c = self.coord_from_pos(col, row)
            self.buttons[(r, c)].config(text="Π", fg="green")
        for col, row in self.board_dict["RED"].items():
            r, c = self.coord_from_pos(col, row)
            self.buttons[(r, c)].config(text="Κ", fg="red")

    def coord_from_pos(self, col, row):
        # Μετατρέπει (col, row) (row: 1-8, 1 = πάνω) σε grid coordinates (r, c) όπου r=0 είναι πάνω
        col_index = ord(col) - ord('a')
        row_index = row - 1
        return (row_index, col_index)

    def pos_from_coord(self, r, c):
        # Αντιστρέφει τις grid coordinates σε (col, row)
        col = chr(c + ord('a'))
        row = r + 1
        return col, row

    def cell_clicked(self, r, c):
        col, row = self.pos_from_coord(r, c)
        current_symbol = self.get_cell_symbol(col, row)
        # Αν το παιχνίδι δεν είναι σε φάση "game", τότε ο χρήστης τοποθετεί πύργους
        if self.mode in ["setup_green", "setup_red"]:
            if current_symbol != " ":
                self.print_message("Το κελί είναι ήδη κατειλημμένο.")
                return
            if self.mode == "setup_green":
                if col in self.board_dict["GREEN"]:
                    self.print_message(f"Εχετε ήδη τοποθετήσει πράσινο πύργο στη στήλη {col}.")
                    return
                self.board_dict["GREEN"][col] = row
                self.print_message(f"Τοποθετήθηκε πράσινος πύργος στη θέση {col}{row}.")
                if len(self.board_dict["GREEN"]) == 8:
                    self.mode = "setup_red"
                    self.print_message("Οι πράσινοι τοποθετήθηκαν. Τώρα τοποθέτησε τους Κόκκινους πύργους (ένας ανά στήλη).")
            elif self.mode == "setup_red":
                if col in self.board_dict["RED"]:
                    self.print_message(f"Έχετε ήδη τοποθετήσει κόκκινο πύργο στη στήλη {col}.")
                    return
                if self.board_dict["GREEN"].get(col, None) == row:
                    self.print_message("Δεν μπορείτε να τοποθετήσετε πύργο στην ίδια θέση με πράσινο.")
                    return
                self.board_dict["RED"][col] = row
                self.print_message(f"Τοποθετήθηκε κόκκινος πύργος στη θέση {col}{row}.")
                if len(self.board_dict["RED"]) == 8:
                    self.mode = "game"
                    self.print_message("Η σκακιέρα διαμορφώθηκε. Ξεκινά το παιχνίδι!")
                    # Αν ο υπολογιστής παίζει πρώτος, κάνουμε κίνηση
                    if self.human_player == "RED":
                        self.master.after(1000, self.computer_move)
        elif self.mode == "game":
            # Στη φάση του παιχνιδιού, όταν ο χρήστης πατάει σε ένα κελί:
            # Εάν το κελί δεν είναι κενό, αγνόησε το click.
            if current_symbol != " ":
                self.print_message("Παρακαλώ κάντε click στο κελί που θελετε να πάει ο πύργος.")
                return
            # Ο χρήστης κάνει κλικ σε ένα κελί και αν υπάρχει έγκυρη κίνηση για τον πύργο του στη συγκεκριμένη στήλη, τότε αυτός μετακινείται.
            if col not in self.board_dict[self.human_player]:
                self.print_message(f"Δεν έχετε πύργο στη στήλη {col}.")
                return
            current_row = self.board_dict[self.human_player][col]
            valid_moves = compute_valid_moves(col, current_row, self.board_dict)
            if row not in valid_moves:
                self.print_message("Η κίνηση δεν είναι έγκυρη βάσει των κανόνων (πιθανόν προσπερνάτε πύργο).")
                return
            self.board_dict[self.human_player][col] = row
            self.print_message(f"Μετακινήσατε τον πύργο στη στήλη {col} από {current_row} σε {row}.")
            self.update_board_gui()
            self.master.after(1000, self.computer_move)
        self.update_board_gui()

    def get_cell_symbol(self, col, row):
        if self.board_dict["GREEN"].get(col, None) == row:
            return "Π"
        elif self.board_dict["RED"].get(col, None) == row:
            return "Κ"
        return " "

    def computer_move(self):
        move = best_computer_move(self.board_dict, self.computer_player, self.human_player)
        if move is None:
            self.print_message("Ο υπολογιστής δεν έχει διαθέσιμες κινήσεις. Νικήσατε!")
            messagebox.showinfo("Τέλος Παιχνιδιού", "Ο υπολογιστής δεν έχει διαθέσιμες κινήσεις. Νικίσατε!")
            self.new_game_btn.pack()
            return
        col = move[0]
        new_row = int(move[1])
        old_row = self.board_dict[self.computer_player][col]
        self.board_dict[self.computer_player][col] = new_row
        self.print_message(f"Ο υπολογιστής μετακίνησε τον πύργο της στήλης {col} από τη γραμμή {old_row} στην {new_row}.")
        self.update_board_gui()
        # Έλεγχος για διαθέσιμες κινήσεις για τον χρήστη
        any_move = False
        for c in self.board_dict[self.human_player]:
            cur = self.board_dict[self.human_player][c]
            if compute_valid_moves(c, cur, self.board_dict):
                any_move = True
                break
        if not any_move:
            self.print_message("Δεν έχετε διαθέσιμες κινήσεις. Χάσατε!")
            messagebox.showinfo("Τέλος Παιχνιδιού", "Δεν έχετε διαθέσιμες κινήσεις. Χάσατε!")
            self.new_game_btn.pack()

    def reset_game(self):
        # Επαναφορά όλων των μεταβλητών για νέο παιχνίδι
        self.mode = None
        self.selected_cell = None
        self.board_dict = {"GREEN": {}, "RED": {}}
        self.new_game_btn.pack_forget()
        self.message_box.configure(state='normal')
        self.message_box.delete("1.0", tk.END)
        self.message_box.configure(state='disabled')
        self.initial_setup()
        self.update_board_gui()

if __name__ == '__main__':
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()
