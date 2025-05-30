import tkinter as tk
import random
import threading
import tkinter.filedialog
import json

# Hasła i kategorie
PHRASES = [
    ("Mikołaj Kopernik", "Słynne postacie"),
    ("Złote Piaski", "Geografia"),
    ("W pustyni i w puszczy", "Literatura"),
    ("Bitwa pod Wiedniem", "Historia"),
    ("Smok Wawelski", "Legenda"),
]

# Koło fortuny
KOLO = [100, 300, 200, 500, 300, 500, 400, 600, 500, 700, 600, 800, 700, 900, 800, 1000, 900, 100, 1000, "BANKRUCTWO", "STOP"]
VOWELS = "AEIOUYĄĘ"

class WheelOfFortune:
    def __init__(self, root):
        self.root = root
        self.players = []
        self.scores = []
        self.current_player = 0
        self.guessed = set()
        self.phrase = ""
        self.category = ""
        self.spin_result = None
        self.has_spun = False
        self.custom_phrases = None
        self.rounds_total = 1
        self.current_round = 1

        self.setup_start_screen()

    def setup_start_screen(self):
        self.root.title("Koło Fortuny - Konfiguracja")

        self.start_frame = tk.Frame(self.root)
        self.start_frame.pack(padx=10, pady=10)

        tk.Label(self.start_frame, text="Podaj liczbę graczy:").grid(row=0, column=0)
        self.num_players_entry = tk.Entry(self.start_frame)
        self.num_players_entry.grid(row=0, column=1)

        tk.Label(self.start_frame, text="Podaj liczbę rund:").grid(row=1, column=0)
        self.num_rounds_entry = tk.Entry(self.start_frame)
        self.num_rounds_entry.insert(0, "1")
        self.num_rounds_entry.grid(row=1, column=1)

        self.submit_button = tk.Button(self.start_frame, text="Dalej", command=self.get_player_names)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.import_button = tk.Button(self.start_frame, text="Importuj plik JSON", command=self.import_json)
        self.import_button.grid(row=3, column=0, columnspan=2, pady=5)

    def import_json(self):
        file_path = tkinter.filedialog.askopenfilename(
            title="Wybierz plik JSON",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Validate format: list of [phrase, category]
                    if isinstance(data, list) and all(isinstance(item, list) and len(item) == 2 for item in data):
                        self.custom_phrases = data
                        self.result_var = getattr(self, "result_var", tk.StringVar())
                        self.result_var.set("Zaimportowano plik z hasłami.")
                    else:
                        tk.messagebox.showerror("Błąd", "Nieprawidłowy format pliku JSON.")
            except Exception as e:
                tk.messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{e}")

    def get_player_names(self):
        try:
            self.num_players = int(self.num_players_entry.get())
            if self.num_players < 1:
                raise ValueError
                
            self.rounds_total = int(self.num_rounds_entry.get())
            if self.rounds_total < 1:
                raise ValueError
        except ValueError:
            return

        for widget in self.start_frame.winfo_children():
            widget.destroy()

        self.player_name_vars = []
        for i in range(self.num_players):
            tk.Label(self.start_frame, text=f"Imię gracza {i+1}:").grid(row=i, column=0)
            name_var = tk.StringVar()
            self.player_name_vars.append(name_var)
            tk.Entry(self.start_frame, textvariable=name_var).grid(row=i, column=1)

        tk.Button(self.start_frame, text="Start gry", command=self.start_game).grid(row=self.num_players, column=0, columnspan=2, pady=10)

    def start_game(self):
        self.players = [var.get() if var.get() else f"Gracz {i+1}" for i, var in enumerate(self.player_name_vars)]
        self.scores = [0] * self.num_players
        self.round_scores = [[] for _ in range(self.num_players)]  # Track scores per round
        self.current_round = 1
        self.start_new_round()

    def start_new_round(self):
        # Save scores from previous round if this isn't the first round
        if self.current_round > 1:
            for i in range(len(self.players)):
                if len(self.round_scores[i]) < self.current_round - 1:
                    self.round_scores[i].append(self.scores[i])
    
        phrases = self.custom_phrases if self.custom_phrases else PHRASES
        self.phrase, self.category = random.choice(phrases)
        self.guessed = set()
        
        # Reset scores for new round
        self.scores = [0] * self.num_players
    
        if hasattr(self, "start_frame"):
            self.start_frame.destroy()
        if hasattr(self, "main_frame"):
            self.main_frame.destroy()
            
        self.setup_game_gui()

    def setup_game_gui(self):
        self.root.title("Koło Fortuny")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Stats frame on the left
        self.stats_frame = tk.Frame(self.main_frame, bd=1, relief=tk.RIDGE)
        self.stats_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        # Create statistics table
        tk.Label(self.stats_frame, text="STATYSTYKI", font=('Arial', 14, 'bold')).pack(pady=5)
        
        # Table header
        header_frame = tk.Frame(self.stats_frame)
        header_frame.pack(fill=tk.X, padx=5)
        
        tk.Label(header_frame, text="Gracz", width=15, font=('Arial', 11, 'bold')).grid(row=0, column=0, padx=5)
        tk.Label(header_frame, text=f"Runda {self.current_round}", width=10, font=('Arial', 11, 'bold')).grid(row=0, column=1, padx=5)
        
        # Create rows for each player
        self.stats_rows = []
        for i, player in enumerate(self.players):
            row_frame = tk.Frame(self.stats_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            name_label = tk.Label(row_frame, text=player, width=15, anchor='w', font=('Arial', 10))
            name_label.grid(row=0, column=0, padx=5)
            
            score_var = tk.StringVar(value="0")
            score_label = tk.Label(row_frame, textvariable=score_var, width=10, font=('Arial', 10))
            score_label.grid(row=0, column=1, padx=5)
            
            self.stats_rows.append((name_label, score_var))
        
        # Values wheel frame
        self.values_frame = tk.Frame(self.main_frame)
        self.values_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        tk.Label(self.values_frame, text="Wartości koła:", font=('Arial', 12, 'bold')).pack(pady=5)
        for value in KOLO:
            tk.Label(self.values_frame, text=str(value), font=('Arial', 10)).pack(pady=1)

        # Game frame (main content)
        self.game_frame = tk.Frame(self.main_frame)
        self.game_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.category_label = tk.Label(self.game_frame, text=f"Kategoria: {self.category}", font=('Arial', 16))
        self.category_label.pack()
        
        self.round_label = tk.Label(self.game_frame, text=f"Runda: {self.current_round}/{self.rounds_total}", font=('Arial', 14))
        self.round_label.pack()

        self.phrase_var = tk.StringVar()
        self.update_phrase_display()
        self.phrase_label = tk.Label(self.game_frame, textvariable=self.phrase_var, font=('Arial', 18))
        self.phrase_label.pack(pady=10)

        self.info_var = tk.StringVar()
        self.info_label = tk.Label(self.game_frame, textvariable=self.info_var, font=('Arial', 14))
        self.info_label.pack()
        self.update_info_label()

        self.result_var = tk.StringVar()
        self.result_label = tk.Label(self.game_frame, textvariable=self.result_var, font=('Arial', 14), fg="blue")
        self.result_label.pack(pady=5)

        self.spin_button = tk.Button(self.game_frame, text="Zakręć kołem", command=self.spin_wheel)
        self.spin_button.pack(pady=5)

        self.guess_entry = tk.Entry(self.game_frame, font=('Arial', 14))
        self.guess_entry.pack(pady=5)

        self.guess_button = tk.Button(self.game_frame, text="Zgadnij literę", command=self.guess_letter, state="disabled")
        self.guess_button.pack(pady=5)

        self.full_guess_entry = tk.Entry(self.game_frame, font=('Arial', 14))
        self.full_guess_entry.pack(pady=5)

        self.full_guess_button = tk.Button(self.game_frame, text="Zgadnij całe hasło", command=self.guess_full_phrase, state="disabled")
        self.full_guess_button.pack(pady=5)

    def update_phrase_display(self):
        display = " ".join([c if not c.isalpha() or c.upper() in self.guessed else "_" for c in self.phrase])
        self.phrase_var.set(display)

    def spin_wheel(self):
        def animate_spin():
            for _ in range(10):
                temp = random.choice(KOLO)
                self.result_var.set(f"Losowanie... {temp}")
                self.root.update()
                self.root.after(100)
            self.spin_result = random.choice(KOLO)
            self.result_var.set(f"Wylosowano: {self.spin_result}")

            if self.spin_result == "BANKRUCTWO":
                self.scores[self.current_player] = 0
                original_color = self.root.cget("bg")
                self.root.config(bg="red")
                self.root.update()
                self.root.after(2000)
                self.root.config(bg=original_color)
                self.result_var.set("BANKRUCTWO! Tracisz wszystkie punkty!")
                self.has_spun = False
                self.next_player()
            elif self.spin_result == "STOP":
                self.result_var.set("STOP – tracisz kolejkę!")
                self.has_spun = False
                self.next_player()
            else:
                self.has_spun = True
                self.guess_button.config(state="normal")
                self.full_guess_button.config(state="normal")

        threading.Thread(target=animate_spin).start()

    def guess_letter(self):
        if not self.has_spun:
            self.result_var.set("Najpierw zakręć kołem!")
            return

        letter = self.guess_entry.get().upper()
        self.guess_entry.delete(0, tk.END)

        if not letter.isalpha() or len(letter) != 1:
            self.result_var.set("Podaj jedną literę.")
            return

        if letter in self.guessed:
            self.result_var.set("Litera już była.")
            return

        if letter in VOWELS:
            if self.scores[self.current_player] < 200:
                self.result_var.set("Za mało punktów na samogłoskę (200 pkt).")
                return
            self.scores[self.current_player] -= 200

        if letter in self.phrase.upper():
            count = self.phrase.upper().count(letter)
            if isinstance(self.spin_result, int) and letter not in VOWELS:
                gained = self.spin_result * count
                self.scores[self.current_player] += gained
            self.result_var.set(f"Litera {letter} występuje {count} raz(y).")
        else:
            self.result_var.set(f"Litera {letter} nie występuje.")
            self.has_spun = False
            self.guess_button.config(state="disabled")
            self.full_guess_button.config(state="disabled")
            self.next_player()

        self.guessed.add(letter)
        self.has_spun = False
        self.guess_button.config(state="disabled")
        self.full_guess_button.config(state="disabled")
        self.update_phrase_display()
        self.update_info_label()

        if "_" not in self.phrase_var.get():
            self.guessed = set(c.upper() for c in self.phrase if c.isalpha())
            self.update_phrase_display()
            self.result_var.set(f"🎆 {self.players[self.current_player]} odgadł hasło i wygrywa! 🎆")
            self.end_game()

    def guess_full_phrase(self):
        if not self.has_spun:
            self.result_var.set("Najpierw zakręć kołem!")
            return

        guess = self.full_guess_entry.get().strip().upper()
        self.full_guess_entry.delete(0, tk.END)

        if guess == self.phrase.upper():
            self.result_var.set(f"🎆 {self.players[self.current_player]} odgadł całe hasło i wygrywa! 🎆")
            self.scores[self.current_player] += 1000
            self.guessed = set(c.upper() for c in self.phrase if c.isalpha())
            self.update_phrase_display()
            self.update_info_label()
            self.end_game()
        else:
            self.result_var.set("Błędne hasło. Tracisz kolejkę.")
            self.has_spun = False
            self.guess_button.config(state="disabled")
            self.full_guess_button.config(state="disabled")
            self.next_player()

    def update_info_label(self):
        name = self.players[self.current_player]
        score = self.scores[self.current_player]
        self.info_var.set(f"Tura gracza: {name} ({score} pkt)")
        
        # Update statistics display
        for i, (_, score_var) in enumerate(self.stats_rows):
            score_var.set(str(self.scores[i]))

    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players
        self.update_info_label()
        self.has_spun = False
        self.guess_button.config(state="disabled")
        self.full_guess_button.config(state="disabled")

    def end_game(self):
        self.spin_button.config(state="disabled")
        self.guess_button.config(state="disabled")
        self.full_guess_button.config(state="disabled")
        
        # Save current round scores
        for i in range(len(self.players)):
            if len(self.round_scores[i]) < self.current_round:
                self.round_scores[i].append(self.scores[i])
    
        # Check if more rounds left
        if self.current_round < self.rounds_total:
            self.current_round += 1
            next_round_btn = tk.Button(
                self.game_frame, 
                text="Następna runda", 
                command=self.start_new_round,
                font=('Arial', 14)
            )
            next_round_btn.pack(pady=10)
        else:
            # Show final winner based on total score across all rounds
            total_scores = [sum(scores) for scores in self.round_scores]
            max_score = max(total_scores)
            winners = [self.players[i] for i, s in enumerate(total_scores) if s == max_score]
            
            # Update statistics table to show final scores
            self.show_final_statistics(total_scores)
            
            if len(winners) == 1:
                self.result_var.set(f"🏆 Zwycięzca gry: {winners[0]} z wynikiem {max_score} pkt! 🏆")
            else:
                self.result_var.set(f"🏆 Remis! Zwycięzcy: {', '.join(winners)} ({max_score} pkt) 🏆")

    def show_final_statistics(self, total_scores):
        # Clear existing stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Create final statistics table
        tk.Label(self.stats_frame, text="KOŃCOWE WYNIKI", font=('Arial', 14, 'bold')).pack(pady=5)
        
        # Table header
        header_frame = tk.Frame(self.stats_frame)
        header_frame.pack(fill=tk.X, padx=5)
        
        tk.Label(header_frame, text="Gracz", width=15, font=('Arial', 11, 'bold')).grid(row=0, column=0, padx=5)
        
        # Add column for each round
        for r in range(1, self.rounds_total + 1):
            tk.Label(header_frame, text=f"R{r}", width=5, font=('Arial', 11, 'bold')).grid(row=0, column=r, padx=2)
        
        # Add total column
        tk.Label(header_frame, text="Suma", width=8, font=('Arial', 11, 'bold')).grid(row=0, column=self.rounds_total+1, padx=5)
        
        # Create rows for each player
        for i, player in enumerate(self.players):
            row_frame = tk.Frame(self.stats_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Player name
            tk.Label(row_frame, text=player, width=15, anchor='w', font=('Arial', 10)).grid(row=0, column=0, padx=5)
            
            # Scores for each round
            for r in range(self.rounds_total):
                round_score = self.round_scores[i][r] if r < len(self.round_scores[i]) else 0
                tk.Label(row_frame, text=str(round_score), width=5, font=('Arial', 10)).grid(row=0, column=r+1, padx=2)
            
            # Total score
            tk.Label(row_frame, text=str(total_scores[i]), width=8, font=('Arial', 10, 'bold')).grid(
                row=0, column=self.rounds_total+1, padx=5)

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.geometry("800x600")  # Set initial window size
    
    # Initialize the game
    game = WheelOfFortune(root)
    
    # Start the main event loop
    root.mainloop()
