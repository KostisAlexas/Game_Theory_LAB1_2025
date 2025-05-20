# sanitation_check.py
import re


def sanitize_positions(input_str, existing_positions=None):
    """
    Ελέγχει την εγκυρότητα της εισόδου για τις θέσεις.
    Μια έγκυρη είσοδος πρέπει:
      - Να αποτελείται από 8 τιμές, διαχωρισμένες με κόμμα.
      - Κάθε τιμή να έχει τη μορφή <στήλη><γραμμή> όπου η στήλη είναι ένα γράμμα (a-h)
        και η γραμμή ένας αριθμός (1-8).
      - Να μην επαναλαμβάνονται οι στήλες.
      - Να περιέχει ακριβώς όλες τις στήλες (a, b, c, d, e, f, g, h).
      - Σε περίπτωση εισόδου για κόκκινες θέσεις, να μην επικαλύπτονται με τις υπάρχουσες θέσεις
        (existing_positions: σύνολο πλειάδων (col, row)).
    Επιστρέφει λεξικό της μορφής { 'a': row, 'b': row, ... } αν η είσοδος είναι έγκυρη, αλλιώς None.
    """
    positions = {}
    entries = [entry.strip() for entry in input_str.split(',')]
    if len(entries) != 8:
        return None
    pattern = re.compile(r'^[a-hA-H][1-8]$')
    for entry in entries:
        if not pattern.fullmatch(entry):
            return None
        col = entry[0].lower()
        row = int(entry[1])
        if col in positions:
            return None
        if existing_positions and (col, row) in existing_positions:
            return None
        positions[col] = row
    if set(positions.keys()) != set(list('abcdefgh')):
        return None
    return positions


def get_valid_positions(prompt, existing_positions=None):
    """
    Ζητάει από το χρήστη να εισάγει τις θέσεις μέχρι να δοθεί έγκυρη είσοδος.
    """
    while True:
        inp = input(prompt).strip()
        pos = sanitize_positions(inp, existing_positions)
        if pos is None:
            print("Μη έγκυρη είσοδος. Παρακαλώ δοκιμάστε ξανά.")
        else:
            return pos


def check_if_move_is_valid(move, player_positions, opponent_positions):
    """
    Ελέγχει αν μια κίνηση είναι έγκυρη για τον παίκτη.

    Η κίνηση πρέπει να έχει τη μορφή "c3" (ένα γράμμα a-h και ένας αριθμός 1-8).
    Επιπλέον:
      - Ο παίκτης πρέπει να έχει πύργο στη στήλη που δηλώνει το γράμμα.
      - Η νέα θέση δεν πρέπει να είναι η ίδια με την τρέχουσα.
      - Η νέα θέση δεν πρέπει να είναι κατειλημμένη από οποιονδήποτε πύργο (είτε του παίκτη είτε του αντιπάλου).
      - Ο πύργος δεν μπορεί να "προσπεράσει" κάποιον άλλο πύργο στη στήλη του. Δηλαδή,
        όλα τα κελιά μεταξύ της τρέχουσας θέσης και της νέας θέσης πρέπει να είναι κενά.

    Επιστρέφει (True, "") αν η κίνηση είναι έγκυρη, αλλιώς (False, <μήνυμα λάθους>).
    """
    move = move.strip().lower()
    if not re.fullmatch(r'[a-h][1-8]', move):
        return (False, "Η μορφή της κίνησης δεν είναι έγκυρη. Δώσε συνδυασμό στήλης (a-h) και γραμμής (1-8).")

    col = move[0]
    try:
        target_row = int(move[1])
    except ValueError:
        return (False, "Η γραμμή πρέπει να είναι αριθμός από 1 έως 8.")

    if col not in player_positions:
        return (False, f"Δεν έχετε πύργο στη στήλη {col}.")

    current_row = player_positions[col]
    if target_row == current_row:
        return (False, "Δεν μετακινείτε τον πύργο στη ίδια θέση.")

    # Έλεγχος αν η νέα θέση είναι ήδη κατειλημένη
    for pos in (player_positions, opponent_positions):
        if pos.get(col, None) == target_row:
            return (False, f"Η θέση {col}{target_row} είναι ήδη κατειλημένη.")

    # Έλεγχος διαδρομής: ο πύργος κινείται κάθετα στη στήλη.
    if current_row < target_row:
        step = 1
    else:
        step = -1
    for row in range(current_row + step, target_row, step):
        if (player_positions.get(col, None) == row) or (opponent_positions.get(col, None) == row):
            return (False,
                    f"Δεν μπορείτε να προσπεράσετε πύργο στη στήλη {col} μεταξύ των θέσεων {current_row} και {target_row}.")

    return (True, "")
