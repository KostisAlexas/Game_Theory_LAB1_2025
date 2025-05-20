# computer_strategy.py
import random

def random_computer_move(board_dict, player, opponent):
    """
    Επιλέγει τυχαία μια έγκυρη κίνηση για τον υπολογιστή.

    Είσοδος:
      - board_dict: Λεξικό με τις τρέχουσες θέσεις των πύργων, π.χ.
                    { 'GREEN': {'a': row, ...}, 'RED': {'a': row, ...} }
      - player: Ο παίκτης που θα κινηθεί ("GREEN" ή "RED").
      - opponent: Ο αντίπαλος παίκτης.

    Επιστρέφει:
      - Μία συμβολοσειρά που περιγράφει την κίνηση, π.χ. "b3", ή
      - None αν δεν υπάρχουν διαθέσιμες κινήσεις.
    """
    valid_moves = []
    for col in board_dict[player]:
        current_row = board_dict[player][col]
        # Έλεγχος προς τα πάνω
        row = current_row - 1
        while row >= 1:
            # Αν υπάρχει πύργος στη θέση αυτή στη στήλη, σταματάμε.
            if row == board_dict[player].get(col, None) or row == board_dict[opponent].get(col, None):
                break
            valid_moves.append(col + str(row))
            row -= 1
        # Έλεγχος προς τα κάτω
        row = current_row + 1
        while row <= 8:
            if row == board_dict[player].get(col, None) or row == board_dict[opponent].get(col, None):
                break
            valid_moves.append(col + str(row))
            row += 1
    if not valid_moves:
        return None
    return random.choice(valid_moves)

def best_computer_move(board_dict, player, opponent):
    """
    Υπολογίζει την καλύτερη κίνηση βάσει στρατηγικής Nim (Poker Nim).

    Λογική:
      1. Για κάθε στήλη (a-h), υπολογίζεται το gap ως:
             gap = |θέση_πύργου1 - θέση_πύργου2| - 1
         δηλαδή ο αριθμός των κενών κελιών μεταξύ των δύο πύργων, ανεξάρτητα από τη σειρά τους.
      2. Υπολογίζεται το συνολικό XOR όλων των gaps.
      3. Αν το XOR είναι 0, τότε δεν υπάρχει νικηφόρα κίνηση και επιστρέφεται τυχαία κίνηση.
      4. Διαφορετικά, για κάθε στήλη που ικανοποιεί:
             (gap XOR nim_sum) < gap
         υπολογίζεται το remove = gap - (gap XOR nim_sum), δηλαδή πόσα κενά θέλουμε να "αφαιρέσουμε".
      5. Αν ο υπολογιστής παίζει ως "GREEN":
             - Αν ο πράσινος πύργος βρίσκεται πάνω από τον κόκκινο (δηλαδή μικρότερος αριθμός γραμμής),
               τότε ο πράσινος μπορεί να κινηθεί προς τα κάτω (αυξάνοντας τον αριθμό γραμμής) χωρίς να ξεπεράσει τον κόκκινο.
             - Αν ο πράσινος βρίσκεται κάτω από τον κόκκινο, τότε μπορεί να κινηθεί προς τα πάνω.
         Αν ο παίκτης είναι "RED", η αντίστροφη λογική εφαρμόζεται.
      6. Επιστρέφει την κίνηση ως string (π.χ. "a5").

    Είσοδος:
      - board_dict: Λεξικό με τις τρέχουσες θέσεις, π.χ.
          { 'GREEN': {'a': row, ...}, 'RED': {'a': row, ...} }
      - player: Ο παίκτης που θα κινηθεί ("GREEN" ή "RED").
      - opponent: Ο αντίπαλος παίκτης.

    Επιστρέφει:
      - Μία συμβολοσειρά που περιγράφει την κίνηση, π.χ. "b3", ή
      - None αν δεν υπάρχουν διαθέσιμες κινήσεις.
    """
    nim_sum = 0
    gaps = {}
    # Για κάθε στήλη, υπολογίζουμε το gap ανεξαρτήτως της διάταξης των πύργων.
    for col in board_dict["GREEN"]:
        pos1 = board_dict["GREEN"][col]
        pos2 = board_dict["RED"][col]
        gap = abs(pos1 - pos2) - 1
        gaps[col] = gap
        nim_sum ^= gap

    if nim_sum == 0:
        return random_computer_move(board_dict, player, opponent)

    # Βρίσκουμε στήλη για την οποία μπορούμε να μειώσουμε το gap ώστε να μηδενιστεί το συνολικό XOR.
    for col, gap in gaps.items():
        target_gap = gap ^ nim_sum
        if target_gap < gap:
            remove = gap - target_gap  # Πόσα κενά θέλουμε να αφαιρέσουμε.
            if player == "GREEN":
                pos_G = board_dict["GREEN"][col]
                pos_R = board_dict["RED"][col]
                # Αν ο πράσινος είναι πάνω από τον κόκκινο, ο πράσινος μπορεί να κινηθεί προς τα κάτω.
                if pos_G < pos_R:
                    new_pos = pos_G + remove
                    if new_pos < pos_R:
                        return col + str(new_pos)
                else:
                    # Αν ο πράσινος είναι κάτω από τον κόκκινο, μπορεί να κινηθεί προς τα πάνω.
                    new_pos = pos_G - remove
                    if new_pos > pos_R:
                        return col + str(new_pos)
            elif player == "RED":
                pos_R = board_dict["RED"][col]
                pos_G = board_dict["GREEN"][col]
                # Αν ο κόκκινος είναι πάνω από τον πράσινο, μπορεί να κινηθεί προς τα κάτω.
                if pos_R < pos_G:
                    new_pos = pos_R + remove
                    if new_pos < pos_G:
                        return col + str(new_pos)
                else:
                    # Αν ο κόκκινος είναι κάτω από τον πράσινο, μπορεί να κινηθεί προς τα πάνω.
                    new_pos = pos_R - remove
                    if new_pos > pos_G:
                        return col + str(new_pos)
    # Εάν δεν βρεθεί κάποια νικηφόρα κίνηση, επιστρέφουμε τυχαία κίνηση.
    return random_computer_move(board_dict, player, opponent)
