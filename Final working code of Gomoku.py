#Final working code of GomokU

import tkinter as tk
from tkinter import messagebox
import math
import random
import copy
import time
import numpy as np
from PIL import Image, ImageTk
import os
import pandas as pd
import csv
import time
import copy

class GomokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku Game")
        self.root.geometry("750x700")  # Set a fixed size for the game window
        self.dataset = pd.DataFrame()  # Initialize as an empty DataFrame
        self.ai_method = "MCTS"  # Default AI method
        self.board_size = 15  # Default board size
        self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = "black"
        self.game_over_flag = False
        self.ai_color = None  # Will be set when the game starts
        self.opponent_color = None  # Will be set when the game starts
        # Define the coordinate map for 15x15 board
        self.coordinate_map = self.create_coordinate_map(self.board_size)
        self.current_game_moves = []  # To store the moves of the current game
        self.game_id = 0  # Unique identifier for each game

        # Load the dataset and images
        self.load_dataset(r"C:\Users\Downloads\gomocup2023results\Standard1\gomoku results\cleaned\path_to_save_cleaned_dataset.csv")
        self.load_images("C:/Users/clean_board.png", 
                         "C:/Users/black_stone.png", 
                         "C:/Users/white_stone.png")

        # Initialize game settings
        self.player1_type = None
        self.player2_type = None

        # Initialize UI components
        self.create_menu()
        self.setup_ui()
    def load_multiple_patterns(self, directory_path):
     try:
        all_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.csv')]
        if not all_files:
            print(f"No CSV files found in directory: {directory_path}")
            return
        
        dataframes = []
        for f in all_files:
            df = pd.read_csv(f)
            if not df.empty:
                # Optional: Add a column to distinguish different patterns
                df['pattern_id'] = f.split('.')[0]  # Assuming the filename indicates the pattern
                dataframes.append(df)
        
        if dataframes:
            self.dataset = pd.concat(dataframes, ignore_index=True)
            print(f"Total records loaded: {len(self.dataset)}")
        else:
            print("All CSV files were empty or could not be loaded.")
            self.dataset = pd.DataFrame()  # Set to an empty DataFrame
     except Exception as e:
        print(f"Failed to load dataset from {directory_path}: {e}")
        self.dataset = pd.DataFrame()  # Set to an empty DataFrame

    def create_coordinate_map(self, board_size):
        """Create a map from a single integer to (row, col) coordinates."""
        coordinate_map = {}
        count = 1
        for row in range(board_size):
            for col in range(board_size):
                coordinate_map[count] = (row, col)
                count += 1
        return coordinate_map
    
    def flatten_board(self, board):
        """Flatten the board into a 1D array of numbers representing the current state."""
        flattened = []
        for row in board:
            flattened.extend([1 if cell == "black" else 2 if cell == "white" else 0 for cell in row])
        return flattened
    
    def log_move(self, x, y):
     move_number = len(self.current_game_moves) + 1
     player = self.current_player
     board_state = self.flatten_board(self.board)  # Flatten the board for saving
     move_data = {
        'Game_ID': self.game_id,
        'Move_Number': move_number,
        'Player': player,
        'x': x,
        'y': y,
        'Board_State': board_state,
        'Winner': None  # Winner will be set at the end of the game
    }
     self.current_game_moves.append(move_data)

    def end_game(self, winner):
     for move in self.current_game_moves:
        move['Winner'] = winner  # Set the winner only at the end of the game
     self.save_game_moves_to_csv()

    def save_game_moves_to_csv(self, filename="gomoku_ai_vs_ai_dataset.csv"):
     for _ in range(3):  # Retry up to 3 times
        try:
            file_exists = os.path.isfile(filename)
            with open(filename, 'a', newline='') as csvfile:
                fieldnames = ['Game_ID', 'Move_Number', 'Player', 'x', 'y', 'Board_State', 'Winner']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()  # Write the header only if the file doesn't exist

                for move in self.current_game_moves:
                    writer.writerow(move)

            self.current_game_moves = []  # Clear the list for the next game
            break  # Exit the loop if the operation is successful
        except PermissionError:
            print("Permission denied when trying to access the file. Retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    def load_dataset(self, directory_path):
        try:
            all_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.csv')]
            if not all_files:
                print(f"No CSV files found in directory: {directory_path}")
                return
            
            dataframes = []
            for f in all_files:
                df = pd.read_csv(f)
                if not df.empty:
                    dataframes.append(df)
            
            if dataframes:
                self.dataset = pd.concat(dataframes, ignore_index=True)
                print(f"Total records loaded: {len(self.dataset)}")
                print(self.dataset.head())  # Print the first few rows to verify loading
            else:
                print("All CSV files were empty or could not be loaded.")
                self.dataset = pd.DataFrame()  # Set to an empty DataFrame
        except Exception as e:
            print(f"Failed to load dataset from {directory_path}: {e}")
            self.dataset = pd.DataFrame()  # Set to an empty DataFrame

    def save_game_moves_to_csv(self, filename="gomoku_ai_vs_ai_dataset.csv"):
     file_exists = os.path.isfile(filename)
     with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Game_ID', 'Move_Number', 'Player', 'x', 'y', 'Board_State', 'Winner']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write the header only if the file doesn't exist

        for move in self.current_game_moves:
            writer.writerow(move)

     self.current_game_moves = []  # Clear the list for the next game
        

    def load_images(self, board_path, black_stone_path, white_stone_path):
        try:
            # Load and resize images with the correct method
            self.board_image = Image.open(board_path).resize((600, 600), Image.LANCZOS)
            self.black_stone_image = Image.open(black_stone_path).resize((40, 40), Image.LANCZOS)
            self.white_stone_image = Image.open(white_stone_path).resize((40, 40), Image.LANCZOS)

            # Convert to PhotoImage for Tkinter
            self.board_photo = ImageTk.PhotoImage(self.board_image)
            self.black_stone_photo = ImageTk.PhotoImage(self.black_stone_image)
            self.white_stone_photo = ImageTk.PhotoImage(self.white_stone_image)

            print("Images loaded successfully.")
        except Exception as e:
            print(f"Error loading images: {e}")
            messagebox.showerror("Error", "Failed to load game images.")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Main Menu", command=self.main_menu)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="Game", menu=game_menu)

        # Modes menu
        modes_menu = tk.Menu(menubar, tearoff=0)
        modes_menu.add_command(label="Human vs. Human", command=lambda: self.new_game("human", "human"))
        modes_menu.add_command(label="Human vs. AI", command=lambda: self.new_game("human", "ai"))
        modes_menu.add_command(label="AI vs. AI", command=self.start_ai_vs_ai_mode)
        menubar.add_cascade(label="Modes", menu=modes_menu)

        # AI Mode Settings menu
        ai_mode_settings_menu = tk.Menu(menubar, tearoff=0)
        ai_mode_settings_menu.add_command(label="Use MCTS AI", command=lambda: self.set_ai_method("MCTS"))
        ai_mode_settings_menu.add_command(label="Use Alpha-Beta Pruning AI", command=lambda: self.set_ai_method("AlphaBeta"))
        ai_mode_settings_menu.add_command(label="Use Policy-Value AI", command=lambda: self.set_ai_method("PolicyValue"))
        menubar.add_cascade(label="AI Mode Settings", menu=ai_mode_settings_menu)

        self.root.config(menu=menubar)
    def check_winner(self, x, y):
     def count_stones(dx, dy):
        count = 0
        nx, ny = x + dx, y + dy
        while 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[nx][ny] == self.current_player:
            count += 1
            nx += dx
            ny += dy
        return count

     directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
     for dx, dy in directions:
        if count_stones(dx, dy) + count_stones(-dx, -dy) + 1 >= 5:
            print(f"Winner found for {self.current_player} at ({x}, {y})")  # Debugging output
            return True
     return False

    
    def switch_player(self):
     if self.current_player == "black":
        self.current_player = "white"
     else:
        self.current_player = "black"
     print(f"Switched player: {self.current_player}")  # Debugging output
     self.status_label.config(text=f"{self.current_player.capitalize()}'s Turn")

    def game_over(self, message):
        messagebox.showinfo("Game Over", message)
        self.start_button.pack()  # Show start button after the game ends
        self.restart_button.pack_forget()  # Hide restart button after the game ends

    def is_first_move(self):
        """Check if this is the first move of the game."""
        return all(cell == "" for row in self.board for cell in row)

    def insert_first_move_into_dataset(self, x, y):
        """Insert the initial move into the first NaN row of the dataset."""
        try:
            # Locate the first NaN row in the dataset
            first_nan_row = self.dataset[self.dataset['x'].isna() & self.dataset['y'].isna()].index[0]
            
            # Insert the initial move (x, y) into this row
            self.dataset.at[first_nan_row, 'x'] = x
            self.dataset.at[first_nan_row, 'y'] = y
            self.dataset.at[first_nan_row, 'value'] = 1  # or any relevant value representing the move
            
            print(f"Inserted initial move ({x}, {y}) into dataset at row {first_nan_row}.")
            
        except IndexError:
            print("No available NaN row found in the dataset to insert the first move.")
        except Exception as e:
            print(f"Error inserting move into dataset: {e}")

    def detect_immediate_threat(self):
     """Check if the opponent is one move away from winning and block it."""
     opponent = "white" if self.current_player == "black" else "black"
     for x in range(self.board_size):
        for y in range(self.board_size):
            if self.board[x][y] == "":
                # Temporarily place the opponent's piece
                self.board[x][y] = opponent
                if self.check_winner(x, y):
                    # Undo the move and return the block position
                    self.board[x][y] = ""
                    return (x, y)
                self.board[x][y] = ""  # Undo the move
     return None
    def predict_move_from_dataset(self):
     if self.dataset.empty:
        print("Dataset is empty or not loaded, unable to predict move.")
        return None

    # Flatten the current board
     current_board_flat = self.flatten_board(self.board)

     best_match = None
     best_similarity = float('inf')  # Initialize with a large value
    
     for _, row in self.dataset.iterrows():
        dataset_board_state = self.parse_board_state(row['board_state_column'])  
        similarity = self.calculate_similarity(current_board_flat, dataset_board_state)
        
        if similarity < best_similarity:
            best_similarity = similarity
            best_match = (row['next_x'], row['next_y'])

     if best_match:
        print(f"Using dataset to predict move: {best_match}")
        return best_match

    # If no suitable move is found, fall back to another strategy
     print("No suitable move found in dataset, falling back to AI.")
     return None
    
    def ai_fallback_strategy(self):
     """Fallback strategy when no other move is found."""
     available_moves = self.get_available_moves()  # Get all available moves
     if available_moves:
        return random.choice(available_moves)
     return None

    def get_available_moves(self):
     """Get a list of all available (empty) positions on the board."""
     available_moves = []
     for x in range(self.board_size):
        for y in range(self.board_size):
            if self.board[x][y] == "":
                available_moves.append((x, y))
     return available_moves

   
    def predict_move_with_fallback(self):
     move = self.predict_move_from_dataset()
    
     if move is None:
        print("No move predicted from dataset, using AI strategy.")
        move = self.ai_fallback_strategy()
    
     return move
    
    def adjust_depth(self):
     empty_cells = sum(row.count("") for row in self.board)
     if self.is_critical():
        return 6  # Increased depth in critical situations
     if empty_cells > 100:
        return 4  # Early game (increased from 3)
     elif empty_cells > 50:
        return 5  # Mid game (increased from 4)
     else:
        return 6  # Late game (increased from 5)

    
    def ai_move_fallback(self):
         
     available_moves = self.get_available_moves()  # Get all available moves
     if available_moves:
         return random.choice(available_moves)
     return None

    
    def ai_move(self):
     if self.game_over_flag:
        return

     if not self.available_moves():
        self.game_over("Draw")
        return

     move = None  # Initialize move

     print(f"AI Move - Current Player: {self.current_player}")  # Debugging output

    # First, attempt to detect and block any immediate threats
     if self.detect_and_block_threat(self.board):
        self.switch_player()  # Ensure player is switched after the AI blocks a threat
        return  # If a move was made to block a threat, end the function

    # Proceed with regular AI move if no immediate threat is detected
     move = self.predict_move_from_dataset()
     if move is None:
        if self.ai_method == "MCTS":
            mcts = MCTSWithPolicyValue(self.board, self.current_player, PolicyValue(self.board, self.current_player, self.root), simulations=1500)
            move = mcts.best_move()
        elif self.ai_method == "AlphaBeta":
            depth = self.adjust_depth()  # Adjust depth dynamically
            alphabeta = AlphaBeta(self.board, self.current_player, depth=depth)
            move = alphabeta.best_move()
        elif self.ai_method == "PolicyValue":
            policy_value = PolicyValue(self.board, self.current_player, self.root)  # Initialize policy_value
            move = policy_value.best_move()

     if move is None:
        print("No valid move found. Ending AI move.")
        return

    # Place the move on the board
     if self.board[move[0]][move[1]] == "":
        self.board[move[0]][move[1]] = self.current_player
        self.draw_board()
        print(f"Board state after move: {self.board}")  # Debugging output
     else:
         print(f"Invalid move: Cell ({move[0]}, {move[1]}) already occupied.")

    # Check if the move results in a win
     if self.check_winner(move[0], move[1]):
        self.game_over(self.current_player + " wins!")
        return  # Prevents the game from continuing

     else:
        self.switch_player()
        # Delay the next move only if AI vs AI
        if (self.current_player == "black" and self.player1_type == "ai") or \
           (self.current_player == "white" and self.player2_type == "ai"):
            self.root.after(1000, self.ai_move)

      
    def log_board_state(self):
     print("Current board state:")
     for row in self.board:
        print(row)

    def ai_vs_ai_move(self):
     if self.game_over_flag:
        self.end_game(self.current_player)
        return

     if not self.available_moves():
        self.game_over("Draw")
        return

     move = None  # Initialize move

     print(f"AI Move - Current Player: {self.current_player}")  # Debugging output

    # First, attempt to detect and block any immediate threats specifically for AI vs AI
     if self.ai_vs_ai_detect_and_block_threat():
        print(f"{self.current_player} blocked a threat.")  # Additional debugging
        self.draw_board()
        self.switch_player()  # Ensure player is switched after the AI blocks a threat
        self.root.after(1000, self.ai_vs_ai_move)  # Schedule the next AI move
        return  # If a move was made to block a threat, end the function

    # Proceed with regular AI move if no immediate threat is detected
     move = self.predict_move_with_fallback()
     if move is None:
        print("No valid move found. Ending AI move.")
        return

    # Place the move on the board
     if self.board[move[0]][move[1]] == "":
        self.board[move[0]][move[1]] = self.current_player
        self.log_move(move[0], move[1])  # Log the move after it's placed
        self.draw_board()
        print(f"Board state after move: {self.board}")  # Debugging output
     else:
        print(f"Invalid move: Cell ({move[0]}, {move[1]}) already occupied.")

    # Check if the move results in a win
     if self.check_winner(move[0], move[1]):
        self.game_over(self.current_player + " wins!")
        self.end_game(self.current_player)  # Ensure the winner is recorded correctly
     else:
        self.switch_player()
        self.root.after(1000, self.ai_vs_ai_move)  # Continue to the next AI move



  

    def start_ai_vs_ai_mode(self):
     self.clear_board()  # Clear the board before starting a new AI vs AI game
     self.new_game("ai", "ai")
     self.start_button.pack()  # Show the start button when AI vs AI mode is selected
     self.root.after(1000, self.ai_vs_ai_move)  # Start AI vs AI moves

    def start_ai_vs_ai(self):
     self.clear_board()  # Clear the board before starting the AI vs AI game
     self.start_button.pack_forget()  # Hide start button when the AI vs AI game starts
     self.root.after(1000, self.ai_vs_ai_move)  # Start AI vs AI moves



    def detect_and_block_threat(self, board):
     for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] == self.opponent_color:
                # Check horizontally, vertically, and diagonally for threats
                if self.check_sequence(board, i, j, 1, 0, 4):  # Horizontal
                    if self.block_move(i, j, 1, 0):
                        return True
                if self.check_sequence(board, i, j, 0, 1, 4):  # Vertical
                    if self.block_move(i, j, 0, 1):
                        return True
                if self.check_sequence(board, i, j, 1, 1, 4):  # Diagonal (bottom-right)
                    if self.block_move(i, j, 1, 1):
                        return True
                if self.check_sequence(board, i, j, -1, 1, 4):  # Diagonal (top-right)
                    if self.block_move(i, j, -1, 1):
                        return True

     return False  # No further threats detected

    def ai_vs_ai_detect_and_block_threat(self):
     opponent = "white" if self.current_player == "black" else "black"
     for i in range(self.board_size):
        for j in range(self.board_size):
            if self.board[i][j] == opponent:
                # Check horizontally, vertically, and diagonally for threats
                if self.check_sequence(self.board, i, j, 1, 0, 3):  # Horizontal
                    if self.ai_vs_ai_block_move(i, j, 1, 0):
                        return True
                if self.check_sequence(self.board, i, j, 0, 1, 3):  # Vertical
                    if self.ai_vs_ai_block_move(i, j, 0, 1):
                        return True
                if self.check_sequence(self.board, i, j, 1, 1, 3):  # Diagonal (bottom-right)
                    if self.ai_vs_ai_block_move(i, j, 1, 1):
                        return True
                if self.check_sequence(self.board, i, j, -1, 1, 3):  # Diagonal (top-right)
                    if self.ai_vs_ai_block_move(i, j, -1, 1):
                        return True

     return False  # No further threats detected

    def check_sequence(self, board, x, y, dx, dy, length):
     sequence_length = 1
     for step in range(1, length):
        new_x = x + step * dx
        new_y = y + step * dy
        
        if 0 <= new_x < self.board_size and 0 <= new_y < self.board_size:
            if board[new_x][new_y] == board[x][y]:
                sequence_length += 1
            else:
                break
        else:
            break
    
     return sequence_length >= 3  # Ensure it detects 3 or more in a row as a critical threat

    def block_move(self, x, y, dx, dy):
     for step in [-1, 4]:
        new_x = x + step * dx
        new_y = y + step * dy
        
        if 0 <= new_x < self.board_size and 0 <= new_y < self.board_size:
            if self.board[new_x][new_y] == "":  # Ensure the spot is empty
                print(f"Blocking move at: ({new_x}, {new_y})")
                self.board[new_x][new_y] = self.current_player
                self.draw_board()
                print(f"Board state after move: {self.board}")  # Log board state
                return True
            else:
                print(f"Invalid move: Cell ({new_x}, {new_y}) already occupied.")  # Debugging output
    
     print("Failed to block move.")
     return False

    def ai_vs_ai_block_move(self, x, y, dx, dy):
     for step in [-1, 4]:
        new_x = x + step * dx
        new_y = y + step * dy

        if 0 <= new_x < self.board_size and 0 <= new_y < self.board_size:
            if self.board[new_x][new_y] == "":  # Ensure the spot is empty
                print(f"AI vs. AI blocking move at: ({new_x}, {new_y})")
                self.board[new_x][new_y] = self.current_player
                self.draw_board()
                return True

     print("Failed to block move in AI vs. AI.")
     return False

    

    def human_move_by_input(self, move_input):
     """Handle moves input as (row, col) integers, e.g., (12, 0)."""
     if (self.current_player == "black" and self.player1_type == "ai") or \
       (self.current_player == "white" and self.player2_type == "ai"):
        print("It's not the human's turn.")
        return

     try:
         move = tuple(map(int, move_input.split(",")))
         if len(move) == 2:
            x, y = move
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                 if self.board[x][y] == "":
                    print(f"Human Move - Current Player: {self.current_player} at ({x}, {y})")
                    self.board[x][y] = self.current_player
                    self.draw_board()

                    if self.is_first_move():
                        self.insert_first_move_into_dataset(x, y)

                    if self.check_winner(x, y):
                        self.game_over(self.current_player + " wins!")
                    else:
                        self.switch_player()
                        if (self.current_player == "black" and self.player1_type == "ai") or \
                           (self.current_player == "white" and self.player2_type == "ai"):
                            self.root.after(1000, self.ai_move)
                 else:
                    print("Invalid move: Cell already occupied.")
            else:
                print("Invalid move: Move out of board bounds.")
         else:
            print("Invalid move format. Please enter as 'x,y'.")
     except ValueError:
        print("Error parsing move input. Ensure it is in 'x,y' format.")

    def on_canvas_click(self, event):
     cell_size = 600 // self.board_size  # Adjust based on board size
     x = event.x // cell_size
     y = event.y // cell_size
     self.human_move_by_input(f"{x},{y}")

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=600, height=600)
        self.canvas.pack()

        self.status_frame = tk.Frame(self.root, relief='sunken', bd=2)
        self.status_frame.pack(fill=tk.X, pady=10)

        self.status_label = tk.Label(self.status_frame, text="Black's Turn", font=("Helvetica", 16))
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.restart_button = tk.Button(self.status_frame, text="Restart", command=self.restart_game, font=("Helvetica", 16), relief='raised', bd=5, bg="lightblue")
        self.restart_button.pack(side=tk.LEFT, padx=10)

        self.start_button = tk.Button(self.status_frame, text="Start Game", command=self.start_ai_vs_ai, font=("Helvetica", 16), relief='raised', bd=5, bg="lightgreen")
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.start_button.pack_forget()  # Hide start button initially

        # Draw the board initially and force canvas update
        self.draw_board()
        self.canvas.update()

    def main_menu(self):
        self.clear_window()

        tk.Label(self.root, text="Gomoku Game", font=("Helvetica", 24, "bold"), fg="darkblue").pack(pady=20)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.create_main_menu_button(button_frame, "Human vs. Human", lambda: self.new_game("human", "human"), "lightblue")
        self.create_main_menu_button(button_frame, "Human vs. AI", lambda: self.new_game("human", "ai"), "lightgreen")
        self.create_main_menu_button(button_frame, "AI vs. AI", self.start_ai_vs_ai_mode, "lightcoral")
        self.create_main_menu_button(button_frame, "AI Mode Settings", self.settings_menu, "lightyellow")
        self.create_main_menu_button(button_frame, "Exit", self.root.quit, "lightgrey")

        # After the main menu is drawn, ensure the board is also drawn if applicable
        self.draw_board()
        self.canvas.update()

    def create_main_menu_button(self, parent, text, command, color):
        button = tk.Button(parent, text=text, command=command, font=("Helvetica", 16), relief='raised', bd=5, bg=color, width=20)
        button.pack(pady=5)

    def settings_menu(self):
        self.clear_window()

        tk.Label(self.root, text="AI Mode Settings", font=("Helvetica", 24, "bold"), fg="darkblue").pack(pady=20)

        self.create_main_menu_button(self.root, "Use MCTS AI", lambda: self.set_ai_method("MCTS"), "lightblue")
        self.create_main_menu_button(self.root, "Use Alpha-Beta Pruning AI", lambda: self.set_ai_method("AlphaBeta"), "lightgreen")
        self.create_main_menu_button(self.root, "Use Policy-Value AI", lambda: self.set_ai_method("PolicyValue"), "lightcoral")
        self.create_main_menu_button(self.root, "Back to Main Menu", self.main_menu, "lightgrey")

    def set_ai_method(self, method):
        self.ai_method = method
        messagebox.showinfo("AI Mode Settings", f"AI method set to {method}")

    def draw_board(self):
        self.canvas.delete("all")  # Clear the Canvas
        # Draw the board image first
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_photo)
        cell_size = 600 // self.board_size  # Adjust based on board size
        for i in range(self.board_size):
            for j in range(self.board_size):
                x0, y0 = i * cell_size, j * cell_size
                if self.board[i][j] == "black":
                    self.canvas.create_image(x0 + cell_size // 2, y0 + cell_size // 2, image=self.black_stone_photo)
                elif self.board[i][j] == "white":
                    self.canvas.create_image(x0 + cell_size // 2, y0 + cell_size // 2, image=self.white_stone_photo)
        #print("Board rendered.")

    def restart_game(self):
        self.game_over_flag = True  # Set a flag to interrupt the AI loop if necessary
        self.new_game(self.player1_type, self.player2_type)  # Reset the game state and UI
        self.game_over_flag = False  # Reset the game_over_flag for the new game
        self.start_button.pack_forget()  # Hide start button after restart
        self.restart_button.config(state=tk.NORMAL)  # Re-enable restart button
        self.status_label.config(text="Black's Turn")  # Reset status label to the initial state
        self.draw_board()  # Ensure board is drawn after restarting

    def clear_board(self):
        self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.canvas.delete("all")
        self.draw_board()

    def new_game(self, player1_type, player2_type):
     self.player1_type = player1_type
     self.player2_type = player2_type
     self.board_size = 15
     self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]
     self.current_player = "black"
     self.status_label.config(text="Black's Turn")
     self.start_button.pack_forget()  # Hide start button when a new game starts
     self.draw_board()
     self.game_id += 1  # Increment the game_id for the new game
     self.current_game_moves = []  # Reset the moves for the new game

    # Set AI color based on player types
     if self.player1_type == "ai":
        self.ai_color = "black"  # AI is black
        self.opponent_color = "white"  # The opponent (human or another AI) is white
     else:
        self.ai_color = "white"  # AI is white
        self.opponent_color = "black"  # The opponent (human) is black

    # Start AI vs. AI mode if both players are AI
     if self.player1_type == "ai" and self.player2_type == "ai":
        self.root.after(1000, self.ai_vs_ai_move)  # Use ai_vs_ai_move for AI vs. AI games
     else:
        if (self.current_player == "black" and self.player1_type == "ai") or \
           (self.current_player == "white" and self.player2_type == "ai"):
            self.root.after(1000, self.ai_move)  # Use ai_move for Human vs. AI games

    def start_ai_vs_ai_mode(self):
        self.clear_board()  # Clear the board before starting a new AI vs AI game
        self.new_game("ai", "ai")
        self.start_button.pack()  # Show the start button when AI vs AI mode is selected

    def start_ai_vs_ai(self):
        self.clear_board()  # Clear the board before starting the AI vs AI game
        self.start_button.pack_forget()  # Hide start button when the AI vs AI game starts
        if self.player1_type == "ai":
            self.root.after(1000, self.ai_move)

    
    def available_moves(self):
        return any("" in row for row in self.board)
    
    def count_consecutive_stones(self, x, y, dx, dy, player):
     """Count the number of consecutive stones of the same player in a direction."""
     count = 0
     nx, ny = x + dx, y + dy
     while 0 <= nx < self.board_size and 0 <= ny < self.board_size:
        if self.board[nx][ny] == player:
            count += 1
            nx += dx
            ny += dy
        else:
            break
     return count
    
    def is_critical(self):
    # Detect if either player is close to winning
     for x in range(self.board_size):
        for y in range(self.board_size):
            if self.board[x][y] == "":
                self.board[x][y] = self.current_player
                if self.check_winner(x, y):
                    self.board[x][y] = ""
                    return True
                self.board[x][y] = ""
     return False  
    def detect_two_or_three_openings(self):
     """Check for sequences of two or three stones that might lead to a winning move."""
     opponent = "white" if self.current_player == "black" else "black"
     for x in range(self.board_size):
        for y in range(self.board_size):
            if self.board[x][y] == "":
                # Check in all four possible directions
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    count = self.count_consecutive_stones(x, y, dx, dy, opponent)
                    if count >= 2:
                        # This is a potential threat (two or three stones in a row)
                        return (x, y)
     return None



def parse_move(self, move_string):
        try:
            if move_string.isdigit():  # If move_string is a single digit
                move_index = int(move_string)
                if move_index in self.coordinate_map:
                    return self.coordinate_map[move_index]
                else:
                    print(f"Invalid move index: {move_string}")
            elif ":" in move_string:  # If move_string is in "row:col" format
                row, col = map(int, move_string.split(":"))
                if 1 <= row <= self.board_size and 1 <= col <= self.board_size:
                    return row - 1, col - 1  # Convert to zero-based indexing
            print(f"Invalid move format or out of bounds: {move_string}")
            return None
        except ValueError as ve:
            print(f"Error parsing move: {move_string} - {str(ve)}")
            return None

def parse_board_state(self, board_string):
        try:
            board_state = list(map(int, board_string.split(",")))
            return board_state
        except ValueError:
            print(f"Error parsing board state: {board_string}")
            return []

def is_similar_board_state(self, current_board_flat, previous_board_state):
        similarity_threshold = 0.9  
        similarity = sum([1 for cb, pb in zip(current_board_flat, previous_board_state) if cb == pb]) / len(current_board_flat)
        return similarity >= similarity_threshold

def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

def show_about(self):
        messagebox.showinfo("About", "Gomoku Game\nCreated with Tkinter")

def replay_game(self, game_id):
        game_moves = self.dataset[self.dataset[0] == game_id]  # Filtering based on Game Type or ID
        self.clear_board()  # Clear the board before replaying the game
        for _, row in game_moves.iterrows():
            move = self.parse_move(row[1])  # Assuming row[1] contains "11:11"
            player = row[2]  # Assuming row[2] contains the player or result indicator
            
            if move is None:
                continue
            
            # Set the player stone on the board
            stone_color = "black" if player == 0 else "white"
            self.board[move[0]][move[1]] = stone_color
            
            self.draw_board()
            self.root.update()
            time.sleep(1)  # Add delay to visualize the replay

        # Assuming the result is in the last row or part of the row
        final_result = game_moves.iloc[-1, 2]  # Modify if needed based on what this column represents
        self.game_over(f"Result: {final_result}")

# Updated Node class to accommodate Policy-Value for rollout

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = self.get_legal_moves(state)
        self.move = move

    def check_winner(self, state, move, player):
        def count_stones(dx, dy):
            count = 0
            nx, ny = move[0] + dx, move[1] + dy
            while 0 <= nx < len(state) and 0 <= ny < len(state[0]) and state[nx][ny] == player:
                count += 1
                nx += dx
                ny += dy
            return count

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            if count_stones(dx, dy) + count_stones(-dx, -dy) + 1 >= 5:
                return True
        return False

    def rollout(self, policy_value_model):
        current_state = copy.deepcopy(self.state)
        player = self.get_player_turn(current_state)
        while True:
            legal_moves = self.get_legal_moves(current_state)
            if len(legal_moves) == 0:
                return 0.5  # Draw
            move = random.choice(legal_moves)
            current_state[move[0]][move[1]] = player
            if self.check_winner(current_state, move, player):
                return 1 if player == "black" else 0
            player = "white" if player == "black" else "black"



    def get_legal_moves(self, state):
        legal_moves = []
        for x in range(len(state)):
            for y in range(len(state[0])):
                if state[x][y] == "":
                    legal_moves.append((x, y))
        return legal_moves

    def expand(self):
        move = self.untried_moves.pop()
        next_state = self.perform_move(self.state, move)
        child_node = Node(next_state, self, move)
        self.children.append(child_node)
        return child_node

    def perform_move(self, state, move):
        new_state = copy.deepcopy(state)
        player = "black" if self.get_player_turn(state) == "black" else "white"
        new_state[move[0]][move[1]] = player
        return new_state

    def get_player_turn(self, state):
        black_count = sum(row.count("black") for row in state)
        white_count = sum(row.count("white") for row in state)
        return "black" if black_count <= white_count else "white"

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=math.sqrt(2)):
        choices_weights = [
            (child.wins / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    
    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1 - result)

    def check_winner(self, state, move, player):
     def count_stones(dx, dy):
        count = 0
        nx, ny = move[0] + dx, move[1] + dy
        while 0 <= nx < len(state) and 0 <= ny < len(state[0]) and state[nx][ny] == player:
            count += 1
            nx += dx
            ny += dy
        return count

     directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
     for dx, dy in directions:
        if count_stones(dx, dy) + count_stones(-dx, -dy) + 1 >= 5:
            return True
     return False

class MCTSWithPolicyValue:
    def __init__(self, state, player, policy_value_model, simulations=1000):
        self.root = Node(state)
        self.player = player
        self.simulations = simulations
        self.policy_value_model = policy_value_model

    def best_move(self):
        for _ in range(self.simulations):
            node = self.select_node()
            if not node.is_fully_expanded():
                node = node.expand()
            result = node.rollout(self.policy_value_model)
            node.backpropagate(result)
        return self.root.best_child(c_param=0).move

    def select_node(self):
        node = self.root
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
        return node
############################################################################    

class AlphaBeta:
    def __init__(self, board, player, depth=3):
        self.board = board
        self.player = player
        self.opponent = "white" if player == "black" else "black"
        self.depth = depth
        self.time_limit = 1.0  # 1 second time limit for the search
    
    def best_move(self):
        self.start_time = time.time()
        _, move = self.alphabeta(self.board, self.depth, -float('inf'), float('inf'), True)
        return move

    def alphabeta(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_terminal(board) or time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None
        
        if maximizing_player:
            max_eval = -float('inf')
            best_moves = []
            for move in self.get_legal_moves(board):
                new_board = self.perform_move(board, move, self.player)
                eval, _ = self.alphabeta(new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_moves = [move]
                elif eval == max_eval:
                    best_moves.append(move)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, random.choice(best_moves)
        else:
            min_eval = float('inf')
            best_moves = []
            for move in self.get_legal_moves(board):
                new_board = self.perform_move(board, move, self.opponent)
                eval, _ = self.alphabeta(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_moves = [move]
                elif eval == min_eval:
                    best_moves.append(move)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, random.choice(best_moves)

    def evaluate(self, board):
        return self.heuristic(board, self.player) - self.heuristic(board, self.opponent)
    
    def block_opponent(self, board, position, player):
     opponent = "white" if player == "black" else "black"
     directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
     score = 0
     for dx, dy in directions:
        if self.is_blocking_move(board, position, (dx, dy), opponent):
            score += 200  # Prioritize blocking
            if self.detect_double_threat(board, position, (dx, dy), player):
                score += 300  # Boost if the block creates a double threat
     return score

    def heuristic(self, board, player):
     score = 0
     for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == player:
                score += self.evaluate_position(board, (x, y), player)
                score += self.block_opponent(board, (x, y), player)
                score += self.pattern_recognition(board, (x, y), player)
     return score

    def evaluate_position(self, board, position, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        for dx, dy in directions:
            score += self.count_stones(board, position, (dx, dy), player)
        return score

    

    def pattern_recognition(self, board, position, player):
        """Recognize specific patterns like open threes or potential winning lines."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        opponent = "white" if player == "black" else "black"
        score = 0
        for dx, dy in directions:
            if self.is_open_three(board, position, (dx, dy), player):
                score += 100  # Boost for creating an open three
            if self.is_winning_line(board, position, (dx, dy), player):
                score += 500  # High score for creating a winning line
            if self.detect_double_threat(board, position, (dx, dy), player):
                score += 300  # Recognize and reward double threats
        return score

    def is_open_three(self, board, position, direction, player):
        """Check if the current move creates an open three."""
        dx, dy = direction
        count = 0
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == player:
                count += 1
            elif board[nx][ny] != "":
                break
            nx += dx
            ny += dy
        return count == 2  # Returns True if exactly three stones are aligned and open

    def is_winning_line(self, board, position, direction, player):
        """Check if the current move creates a winning line."""
        dx, dy = direction
        count = 1  # Start with 1 since the current stone is already placed
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == player:
                count += 1
            else:
                break
            nx += dx
            ny += dy
        # Check in the opposite direction
        nx, ny = position[0] - dx, position[1] - dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == player:
                count += 1
            else:
                break
            nx -= dx
            ny -= dy
        return count >= 5  # Returns True if five or more stones are aligned

    def detect_double_threat(self, board, position, direction, player):
        """Detect if the current move creates a double threat."""
        threat_count = 0
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if self.is_open_three(board, position, (dx, dy), player):
                threat_count += 1
        return threat_count >= 2  # Returns True if there are two or more open threes
    def block_opponent(self, board, position, player):
     opponent = "white" if player == "black" else "black"
     directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
     score = 0
     for dx, dy in directions:
        if self.is_blocking_move(board, position, (dx, dy), opponent):
           score += 200  # Increased to prioritize blocking over offensive play
     return score

    def is_blocking_move(self, board, position, direction, opponent):
        dx, dy = direction
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == opponent:
                return True
            nx += dx
            ny += dy
        return False

    def count_stones(self, board, position, direction, player):
        dx, dy = direction
        count = 0
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]) and board[nx][ny] == player:
            count += 1
            nx += dx
            ny += dy
        return count

    def is_winner(self, board, player):
        for x in range(len(board)):
            for y in range(len(board[0])):
                if board[x][y] == player:
                    if self.check_winner(board, (x, y), player):
                        return True
        return False

    def check_winner(self, state, move, player):
        def count_stones(dx, dy):
            count = 0
            nx, ny = move[0] + dx, move[1] + dy
            while 0 <= nx < len(state) and 0 <= ny < len(state[0]) and state[nx][ny] == player:
                count += 1
                nx += dx
                ny += dy
            return count

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            if count_stones(dx, dy) + count_stones(-dx, -dy) + 1 >= 5:
                return True
        return False

    def is_terminal(self, board):
        return self.is_winner(board, self.player) or self.is_winner(board, self.opponent) or all(cell != "" for row in board for cell in row)

    def get_legal_moves(self, state):
        legal_moves = []
        for x in range(len(state)):
            for y in range(len(state[0])):
                if state[x][y] == "":
                    legal_moves.append((x, y))
        return legal_moves

    def perform_move(self, state, move, player):
        new_state = copy.deepcopy(state)
        new_state[move[0]][move[1]] = player
        return new_state

#############################################################

class PolicyValue:
    def __init__(self, board, player, root):
        self.board = board
        self.player = player
        self.opponent = "white" if player == "black" else "black"
        self.root = root  # Reference to Tkinter root for scheduling AI moves
        self.game_over_flag = False  # Initialize the game_over_flag

    def get_legal_moves(self, state):
        legal_moves = []
        for x in range(len(state)):
            for y in range(len(state[0])):
                if state[x][y] == "":
                    legal_moves.append((x, y))
        return legal_moves

    def heuristic(self, board, player):
        score = 0
        for x in range(len(board)):
            for y in range(len(board[0])):
                if board[x][y] == player:
                    score += self.evaluate_position(board, (x, y), player)
                    score += self.block_opponent(board, (x, y), player)
                    score += self.pattern_recognition(board, (x, y), player)
        return score

    def evaluate_position(self, board, position, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        for dx, dy in directions:
            score += self.count_stones(board, position, (dx, dy), player)
        return score

    def pattern_recognition(self, board, position, player):
        """Recognize specific patterns like open threes or potential winning lines."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        opponent = "white" if player == "black" else "black"
        score = 0
        for dx, dy in directions:
            if self.is_open_three(board, position, (dx, dy), player):
                score += 100  # Boost for creating an open three
            if self.is_winning_line(board, position, (dx, dy), player):
                score += 500  # High score for creating a winning line
            if self.detect_double_threat(board, position, (dx, dy), player):
                score += 300  # Recognize and reward double threats
        return score

    def is_open_three(self, board, position, direction, player):
        """Check if the current move creates an open three."""
        dx, dy = direction
        count = 0
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == player:
                count += 1
            elif board[nx][ny] != "":
                break
            nx += dx
            ny += dy
        return count == 2  # Returns True if exactly three stones are aligned and open

    def is_winning_line(self, board, position, direction, player):
        """Check if the current move creates a winning line."""
        dx, dy = direction
        count = 1  # Start with 1 since the current stone is already placed
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == player:
                count += 1
            else:
                break
            nx += dx
            ny += dy
        # Check in the opposite direction
        nx, ny = position[0] - dx, position[1] - dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == player:
                count += 1
            else:
                break
            nx -= dx
            ny -= dy
        return count >= 5  # Returns True if five or more stones are aligned

    def detect_double_threat(self, board, position, direction, player):
        """Detect if the current move creates a double threat."""
        threat_count = 0
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if self.is_open_three(board, position, (dx, dy), player):
                threat_count += 1
        return threat_count >= 2  # Returns True if there are two or more open threes

    def is_blocking_move(self, board, position, direction, opponent):
        dx, dy = direction
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
            if board[nx][ny] == opponent:
                return True
            nx += dx
            ny += dy
        return False

    def count_stones(self, board, position, direction, player):
        dx, dy = direction
        count = 0
        nx, ny = position[0] + dx, position[1] + dy
        while 0 <= nx < len(board) and 0 <= ny < len(board[0]) and board[nx][ny] == player:
            count += 1
            nx += dx
            ny += dy
        return count

    def best_move(self):
        if self.is_terminal(self.board):
            return None  # Prevent further moves if the game is over
        legal_moves = self.get_legal_moves(self.board)
        policy, value = self.policy_value(self.board)
        best_move = max(legal_moves, key=lambda move: policy[move[0]][move[1]])
        return best_move

    def policy_value(self, board):
        # Generate a simplified mock policy-value prediction
        size = len(board)
        policy = np.random.rand(size, size)  # Random policy distribution over the board
        value = np.random.rand()  # Random value prediction
        return policy, value

    def perform_move(self, state, move, player):
        if move is None:
            return state  # Do nothing if move is None
        new_state = copy.deepcopy(state)
        new_state[move[0]][move[1]] = player
        return new_state

    def check_winner(self, state, move, player):
        def count_stones(dx, dy):
            count = 0
            nx, ny = move[0] + dx, move[1] + dy
            while 0 <= nx < len(state) and 0 <= ny < len(state[0]) and state[nx][ny] == player:
                count += 1
                nx += dx
                ny += dy
            return count

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            if count_stones(dx, dy) + count_stones(-dx, -dy) + 1 >= 5:
                return True
        return False

    def is_winner(self, board, player):
        for x in range(len(board)):
            for y in range(len(board[0])):
                if board[x][y] == player:
                    if self.check_winner(board, (x, y), player):
                        return True
        return False
    
    def is_terminal(self, board):
        return self.is_winner(board, self.player) or self.is_winner(board, self.opponent) or all(cell != "" for row in board for cell in row)

    def ai_vs_ai_move(self):
        if self.game_over_flag:
            return  # Stop further moves if the game is over
        
        if self.is_terminal(self.board):
            return  # Stop further moves if the game is over

        move = self.best_move()
        if move:
            self.board = self.perform_move(self.board, move, self.player)
            if self.check_winner(self.board, move, self.player):
                print(f"Winner detected: {self.player} at move {move}")
                self.game_over(self.player)  # Handle game over scenario
                self.game_over_flag = True  # Set the flag to prevent further moves
                return
            # Switch player and continue if no winner
            self.player, self.opponent = self.opponent, self.player
            self.root.after(1000, self.ai_vs_ai_move)  # Delay and continue AI vs AI move

    def game_over(self, winner):
        print(f"Game over: {winner} wins")
        self.game_over_flag = True  # Set flag to prevent further moves
        # Save results, update UI, etc.


if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuGame(root)
    root.mainloop()


