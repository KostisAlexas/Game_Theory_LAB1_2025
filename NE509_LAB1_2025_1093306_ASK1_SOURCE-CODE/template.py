# template.py
import random
from sanitation_check import get_valid_positions, check_if_move_is_valid
from computer_strategy import best_computer_move, random_computer_move


def random_board_setup():
    """
    Δημιουργεί τυχαία board_dict με 8 στήλες (a-h).
    Σε κάθε στήλη τοποθετείται τυχαία ένας πράσινος (GREEN) και ένας κόκκινος (RED) πύργος,
    με τιμές γραμμών από 1 έως 8, όπου οι γραμμές μετρούνται από πάνω (1) προς τα κάτω (8).
    """
    board_dict = {"GREEN": {}, "RED": {}}
    for idx, col in enumerate('abcdefgh'):
        rows = random.sample(range(1, 9), 2)  # Επιλογή δύο μοναδικών γραμμών από 1 έως 8.
        board_dict["GREEN"][col] = rows[0]
        board_dict["RED"][col] = rows[1]
    return board_dict


def user_board_setup():
    """
    Επιτρέπει στον χρήστη να ορίσει τις θέσεις των πύργων χειροκίνητα με επαλήθευση.
    Εάν ο χρήστης δεν επιθυμεί να καθορίσει χειροκίνητα, δημιουργείται τυχαία board_dict.
    Επιστρέφει board_dict με τη μορφή:
      { "GREEN": {'a': row, ...}, "RED": {'a': row, ...} }
    """
    choice = input("Θέλεις να φτιάξεις το board μόνος σου; (y/n): ").strip().lower()
    if choice == 'n':
        return random_board_setup()

    # Λήψη θέσεων για τους πράσινους πύργους
    green_positions = get_valid_positions(
        "Δώσε τις θέσεις των Πράσινων πύργων (π.χ. a1,b2,c3,d4,e5,f6,g7,h8): "
    )

    # Δημιουργούμε σύνολο κατειλημμένων θέσεων για επαλήθευση στα κόκκινα.
    occupied = {(col, row) for col, row in green_positions.items()}

    # Λήψη θέσεων για τους κόκκινους πύργους, χωρίς επικάλυψη με τους πράσινους.
    red_positions = get_valid_positions(
        "Δώσε τις θέσεις των Κόκκινων πύργων (π.χ. a8,b7,c6,d5,e4,f3,g2,h1): ",
        existing_positions=occupied
    )

    board_dict = {"GREEN": green_positions, "RED": red_positions}
    return board_dict


def build_board_list(board_dict):
    """
    Δημιουργεί μια λίστα λιστών (8x8) για εκτύπωση του board.
    Τα κελιά γεμίζουν με 'Π' για πράσινο, 'Κ' για κόκκινο και ' ' για κενό.
    Οι γραμμές αριθμούνται από 1 (επάνω) έως 8 (κάτω).
    """
    board = [[' ' for _ in range(8)] for _ in range(8)]
    col_to_index = {letter: idx for idx, letter in enumerate('abcdefgh')}
    for player, symbol in (("GREEN", 'Π'), ("RED", 'Κ')):
        for col, row in board_dict[player].items():
            # Μετατροπή: γραμμή 1 → δείκτης 0, γραμμή 8 → δείκτης 7.
            row_idx = row - 1
            col_idx = col_to_index[col]
            board[row_idx][col_idx] = symbol
    return board


def print_board(board):
    """
    Εκτυπώνει το board με text art, με ξεκάθαρα διαχωρισμένα τα κελιά.
    Οι στήλες εμφανίζονται ως a-h και οι γραμμές από 1 (επάνω) έως 8 (κάτω).
    """
    col_labels = '     ' + '   '.join(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
    print(col_labels)
    print('   +' + '---+' * 8)
    for i, row in enumerate(board):
        row_number = i + 1  # 1 έως 8
        row_str = f" {row_number} | " + " | ".join(row) + " |"
        print(row_str)
        print('   +' + '---+' * 8)


def valid_moves_for_column(col, current_row, board_dict):
    """
    Επιστρέφει μια λίστα με έγκυρες γραμμές (ως αριθμούς) στις οποίες μπορεί να κινηθεί ο πύργος
    στη στήλη col, δεδομένης της τρέχουσας θέσης current_row.

    Η κίνηση επιτρέπεται μόνο κάθετα, προς τα πάνω ή προς τα κάτω, χωρίς να υπάρχουν
    πύργοι (είτε δικός του είτε του αντιπάλου) στα ενδιάμεσα κελιά.
    """
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


def any_valid_moves(player, board_dict):
    """
    Ελέγχει αν ο παίκτης έχει διαθέσιμες κινήσεις σε οποιαδήποτε στήλη.
    Επιστρέφει True αν υπάρχει τουλάχιστον μία έγκυρη κίνηση, αλλιώς False.
    """
    for col in board_dict[player]:
        current_row = board_dict[player][col]
        moves = valid_moves_for_column(col, current_row, board_dict)
        if moves:
            return True
    return False


def update_board_dict(board_dict, player, move):
    """
    Ενημερώνει το board_dict για την κίνηση του παίκτη.
    Η κίνηση δίνεται ως string, π.χ. "c3". Μετακινεί τον πύργο του παίκτη στη νέα γραμμή.
    Επιστρέφει το ενημερωμένο board_dict.
    """
    col = move[0]
    new_row = int(move[1])
    board_dict[player][col] = new_row
    return board_dict


def game_loop():
    """
    Κύριος βρόχος παιχνιδιού.

    1. Δημιουργείται το board_dict είτε με τυχαία είτε με χειροκίνητη εισαγωγή από τον χρήστη.
    2. Ο χρήστης επιλέγει αν θέλει να παίξει πρώτος ως Πράσινος ή δεύτερος ως Κόκκινος.
       Σημείωση: Αν ο χρήστης επιλέξει να παίξει δεύτερος (Κόκκινος),
                ο υπολογιστής παίζει πρώτος και, σύμφωνα με τους κανόνες του Poker Nim,
                παίζει με τους Πράσινους.
    3. Εναλλάσσονται οι κινήσεις μεταξύ χρήστη και υπολογιστή:
         - Αν ο χρήστης παίζει, ζητείται κίνηση και γίνεται έλεγχος εγκυρότητας.
         - Αν ο υπολογιστής παίζει, εκτελείται η στρατηγική (ή τυχαία κίνηση ως fallback).
         - Μετά από κάθε κίνηση, ελέγχεται αν ο παίκτης που έπαιξε έχει διαθέσιμες μελλοντικές κινήσεις.
         - Αν όχι, ο παίκτης χάνει και το παιχνίδι τερματίζεται.
    """
    board_dict = user_board_setup()
    board = build_board_list(board_dict)
    print_board(board)

    choice = input(
        "Θέλεις να παίξεις πρώτος ως Πράσινος ή δεύτερος ως Κόκκινος; (πληκτρολόγησε '1' για Πράσινος, '2' για Κόκκινος): ").strip()
    if choice == '1':
        # Αν παίζει πρώτος, ο χρήστης παίζει ως Πράσινος και ο υπολογιστής με τα Κόκκινα.
        human_player = "GREEN"
        computer_player = "RED"
    else:
        # Αν παίζει δεύτερος, ο υπολογιστής παίζει πρώτος ως Πράσινος και ο χρήστης με τα Κόκκινα.
        human_player = "RED"
        computer_player = "GREEN"

    # Ορίζουμε ποιος είναι ο τρέχων παίκτης (ξεκινάει ο πρώτος που παίζει)
    current_player = computer_player if choice == '2' else human_player

    while True:
        # Έλεγχος αν ο τρέχων παίκτης έχει διαθέσιμες κινήσεις.
        if not any_valid_moves(current_player, board_dict):
            if current_player == human_player:
                print("Δεν έχετε διαθέσιμες κινήσεις. Χάσατε!")
            else:
                print("Ο υπολογιστής δεν έχει διαθέσιμες κινήσεις. Νικητήσατε!")
            break

        if current_player == human_player:
            # Κίνηση χρήστη
            valid_move = False
            while not valid_move:
                move = input("Δώσε κίνηση (π.χ. c3): ").strip().lower()
                if len(move) != 2:
                    print("Λανθασμένη μορφή κίνησης. Δοκιμάστε πάλι.")
                    continue
                col = move[0]
                if col not in board_dict[human_player]:
                    print(f"Δεν έχετε πύργο στη στήλη {col}.")
                    continue
                current_row = board_dict[human_player][col]
                # Επιλέγουμε τον αντίστοιχο αντίπαλο παίκτη για έλεγχο.
                other_player = "GREEN" if human_player == "RED" else "RED"
                is_valid, error_msg = check_if_move_is_valid(move, board_dict[human_player], board_dict[other_player])
                if not is_valid:
                    print(error_msg)
                    continue
                target_row = int(move[1])
                available = valid_moves_for_column(col, current_row, board_dict)
                if target_row not in available:
                    print(f"Η κίνηση στο {move} δεν είναι δυνατή λόγω εμπλοκής άλλου πύργου.")
                    continue
                valid_move = True
            board_dict = update_board_dict(board_dict, human_player, move)
            print(f"Επιλέξατε κίνηση: {move}")
        else:
            # Κίνηση υπολογιστή χρησιμοποιώντας στρατηγική Nim.
            move = best_computer_move(board_dict, computer_player, human_player)
            if move is None:
                print("Ο υπολογιστής δεν έχει διαθέσιμες κινήσεις. Νικήσατε!")
                break
            board_dict = update_board_dict(board_dict, computer_player, move)
            print(f"Ο υπολογιστής μετακινεί τον πύργο του από τη στήλη {move[0]} στην γραμμή {move[1]}.")

        board = build_board_list(board_dict)
        print_board(board)

        # Εναλλαγή παίκτη
        current_player = human_player if current_player == computer_player else computer_player


if __name__ == '__main__':
    game_loop()
