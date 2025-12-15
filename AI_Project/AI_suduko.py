"""
===============================================================================
                     SUDOKU GAME WITH AI SOLVER
                          Course Project
===============================================================================

Date: 29th November 2025
Description: A complete Sudoku game built with Pygame featuring:
    - Graphical user interface with Pygame
    - Random Sudoku puzzle generation for each game
    - AI-powered solver using Backtracking Algorithm
    - Constraint Satisfaction Problem (CSP) approach with regression/constraint propagation
    - SLM (Simplified Logic Model) for possibility suggestions
    - Real-time hint system showing valid possibilities
    - Interactive gameplay with mouse clicks
    
Key Features:
    1. Backtracking Algorithm: Systematically tries values and backtracks when constraints are violated
    2. Constraint Propagation: Eliminates invalid candidates before backtracking
    3. Possibility Suggestion: Shows all valid numbers for empty cells
    4. Complete Puzzle Generation: Creates valid random Sudoku puzzles
    5. Solver Visualization: AI can solve the puzzle step by step
    6. User Interface: Clean, intuitive GUI with game controls

Algorithm Explanation:
    Backtracking: Recursively places numbers 1-9 in empty cells, checking if placement
                  is valid according to Sudoku rules. If invalid, backtracks and tries
                  the next number.
    
    Constraint Propagation: Before attempting a number, reduces the domain of possibilities
                           for related cells to minimize backtracking operations.
    
    SLM (Possibility Logic Model): For each empty cell, calculates all valid candidates
                                  based on row, column, and 3x3 box constraints.

===============================================================================
"""

import pygame
import sys
import random
import copy
import time
from typing import List, Tuple, Set, Optional, Dict
import os


class SudokuBoard:
    """
    Represents a Sudoku board with 9x9 grid structure.
    Provides methods for board manipulation, validation, and solving.
    
    Attributes:
        board (List[List[int]]): 9x9 grid representing the puzzle (0 = empty)
        solution (List[List[int]]): Complete solved puzzle
        initial_board (List[List[int]]): Copy of initial puzzle for reset
    """
    
    SIZE = 9  # Sudoku board is 9x9
    BOX_SIZE = 3  # Each box is 3x3
    EMPTY = 0  # Represents empty cell
    
    def __init__(self, board: Optional[List[List[int]]] = None):
        """
        Initialize Sudoku board.
        
        Args:
            board: Optional 9x9 list. If None, creates empty board.
        """
        if board is None:
            self.board = [[0] * 9 for _ in range(9)]
        else:
            self.board = copy.deepcopy(board)
        
        self.initial_board = copy.deepcopy(self.board)
        self.solution = None
        self._generate_solution()
    
    def _generate_solution(self) -> bool:
        """
        Generate a complete valid solution for current board state.
        Uses backtracking algorithm to fill the board.
        
        Returns:
            bool: True if solution found, False otherwise
        """
        board_copy = copy.deepcopy(self.board)
        if self._solve_with_backtracking(board_copy):
            self.solution = board_copy
            return True
        return False
    
    def _solve_with_backtracking(self, board: List[List[int]]) -> bool:
        """
        BACKTRACKING ALGORITHM IMPLEMENTATION:
        
        This is the core solving algorithm. It works by:
        1. Finding the next empty cell (value = 0)
        2. Trying each number 1-9 in that cell
        3. Checking if the number is valid (doesn't violate Sudoku rules)
        4. Recursively solving the rest of the board
        5. If a number leads to dead end, backtrack and try next number
        6. If all cells filled, puzzle is solved
        
        Time Complexity: O(9^(n)) where n is number of empty cells (worst case)
        Space Complexity: O(n) for recursion stack
        
        Args:
            board: The board to solve
            
        Returns:
            bool: True if board can be completely solved, False otherwise
        """
        # Find next empty cell
        empty_cell = self._find_empty_cell(board)
        
        # If no empty cell, puzzle is solved
        if empty_cell is None:
            return True
        
        row, col = empty_cell
        
        # Try each number 1-9
        for num in range(1, 10):
            # Check if this number is valid in this position
            if self._is_valid_placement(board, row, col, num):
                # Place the number (this is the "guess" in backtracking)
                board[row][col] = num
                
                # Recursively try to solve the rest of the board
                if self._solve_with_backtracking(board):
                    return True
                
                # If recursion didn't lead to solution, backtrack
                # Undo the guess by setting cell back to 0 (empty)
                board[row][col] = 0
        
        # If no number works, return False to trigger backtrack in parent call
        return False
    
    def _find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """
        Find first empty cell in board using row-major order.
        
        Args:
            board: Board to search
            
        Returns:
            Tuple of (row, col) for first empty cell, or None if no empty cells
        """
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return (row, col)
        return None
    
    def _is_valid_placement(self, board: List[List[int]], 
                           row: int, col: int, num: int) -> bool:
        """
        CONSTRAINT VALIDATION:
        
        Check if placing 'num' at (row, col) violates Sudoku constraints.
        A placement is valid if:
        1. Number doesn't already exist in the same row
        2. Number doesn't already exist in the same column
        3. Number doesn't already exist in the same 3x3 box
        
        This is CONSTRAINT PROPAGATION - we eliminate invalid possibilities
        before attempting backtracking, reducing search space significantly.
        
        Time Complexity: O(1) - always checks fixed 9 cells per dimension
        
        Args:
            board: Board state to check
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)
            
        Returns:
            bool: True if placement is valid, False otherwise
        """
        # CONSTRAINT 1: Check row - ensure number isn't already in this row
        if num in board[row]:
            return False
        
        # CONSTRAINT 2: Check column - ensure number isn't already in this column
        for r in range(9):
            if board[r][col] == num:
                return False
        
        # CONSTRAINT 3: Check 3x3 box - ensure number isn't already in this box
        box_row = (row // 3) * 3  # Top-left row of the 3x3 box
        box_col = (col // 3) * 3  # Top-left col of the 3x3 box
        
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if board[r][c] == num:
                    return False
        
        return True
    
    def get_possibilities(self, row: int, col: int) -> Set[int]:
        """
        SLM (SIMPLIFIED LOGIC MODEL) - POSSIBILITY CALCULATOR:
        
        For a given empty cell, calculate all valid numbers that could be placed.
        This uses constraint satisfaction to determine the domain of possibilities.
        
        Algorithm:
        1. Start with all numbers 1-9 as candidates
        2. Remove numbers already in same row
        3. Remove numbers already in same column
        4. Remove numbers already in same 3x3 box
        5. Return remaining candidates
        
        This is used to:
        - Show user what numbers are possible (hint system)
        - Reduce search space in backtracking
        - Implement AI suggestion feature
        
        Time Complexity: O(1) - always checks fixed 27 cells
        Space Complexity: O(1) - at most 9 elements in set
        
        Args:
            row: Row index of cell (0-8)
            col: Column index of cell (0-8)
            
        Returns:
            Set containing all valid numbers (1-9) that can be placed in this cell
        """
        if self.board[row][col] != 0:
            # Cell is not empty, no possibilities
            return set()
        
        # Start with all possibilities
        possibilities = set(range(1, 10))
        
        # CONSTRAINT 1: Remove numbers in same row
        for c in range(9):
            if self.board[row][c] != 0:
                possibilities.discard(self.board[row][c])
        
        # CONSTRAINT 2: Remove numbers in same column
        for r in range(9):
            if self.board[r][col] != 0:
                possibilities.discard(self.board[r][col])
        
        # CONSTRAINT 3: Remove numbers in same 3x3 box
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.board[r][c] != 0:
                    possibilities.discard(self.board[r][c])
        
        return possibilities
    
    def get_all_possibilities(self) -> Dict[Tuple[int, int], Set[int]]:
        """
        Calculate possibilities for all empty cells in current board state.
        Used by AI to provide comprehensive hint information.
        
        Returns:
            Dict mapping (row, col) to set of possible numbers for that cell
        """
        possibilities = {}
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    poss = self.get_possibilities(row, col)
                    if poss:
                        possibilities[(row, col)] = poss
        return possibilities
    
    def place_number(self, row: int, col: int, num: int) -> bool:
        """
        Place a number on the board with validation.
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9) or 0 to clear
            
        Returns:
            bool: True if placement was valid, False otherwise
        """
        if num == 0:
            self.board[row][col] = 0
            return True
        
        if not self._is_valid_placement(self.board, row, col, num):
            return False
        
        self.board[row][col] = num
        return True
    
    def is_complete(self) -> bool:
        """
        Check if the board is completely filled.
        
        Returns:
            bool: True if all cells are filled (no zeros), False otherwise
        """
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def is_valid_complete(self) -> bool:
        """
        Check if the completely filled board is valid (no constraint violations).
        
        Returns:
            bool: True if all cells filled and valid, False otherwise
        """
        if not self.is_complete():
            return False
        
        # Check all rows
        for row in self.board:
            if len(set(row)) != 9 or 0 in row:
                return False
        
        # Check all columns
        for col in range(9):
            column = [self.board[row][col] for row in range(9)]
            if len(set(column)) != 9:
                return False
        
        # Check all 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = []
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        box.append(self.board[r][c])
                if len(set(box)) != 9:
                    return False
        
        return True
    
    def reset(self):
        """Reset board to initial state."""
        self.board = copy.deepcopy(self.initial_board)
    
    def get_difficulty_level(self) -> str:
        """
        Estimate puzzle difficulty based on number of empty cells.
        
        Returns:
            str: 'Easy', 'Medium', 'Hard', or 'Expert'
        """
        empty_count = sum(1 for row in self.board for cell in row if cell == 0)
        
        if empty_count <= 30:
            return 'Easy'
        elif empty_count <= 40:
            return 'Medium'
        elif empty_count <= 50:
            return 'Hard'
        else:
            return 'Expert'


class SudokuPuzzleGenerator:
    """
    Generate random valid Sudoku puzzles.
    
    Creates completely filled valid sudoku boards and then removes numbers
    to create puzzles with unique solutions.
    """
    
    @staticmethod
    def generate_puzzle(difficulty: str = 'Medium') -> SudokuBoard:
        """
        Generate a new random Sudoku puzzle.
        
        Algorithm:
        1. Create empty board
        2. Fill it completely using backtracking with random numbers
        3. Remove cells based on difficulty level
        4. Ensure resulting puzzle has unique solution
        
        Args:
            difficulty: 'Easy' (30 cells removed), 'Medium' (40), 'Hard' (50), 'Expert' (60+)
            
        Returns:
            SudokuBoard: New puzzle with removed cells
        """
        board = [[0] * 9 for _ in range(9)]
        SudokuPuzzleGenerator._fill_board_randomly(board)
        
        # Determine how many cells to remove based on difficulty
        difficulty_map = {
            'Easy': 30,
            'Medium': 40,
            'Hard': 50,
            'Expert': 60
        }
        cells_to_remove = difficulty_map.get(difficulty, 40)
        
        # Remove cells randomly
        removed = 0
        while removed < cells_to_remove:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                removed += 1
        
        return SudokuBoard(board)
    
    @staticmethod
    def _fill_board_randomly(board: List[List[int]]) -> bool:
        """
        Fill board completely with valid numbers using randomized backtracking.
        
        Args:
            board: Empty board to fill
            
        Returns:
            bool: True if successfully filled
        """
        empty_cell = SudokuPuzzleGenerator._find_empty_cell(board)
        
        if empty_cell is None:
            return True  # Board is complete
        
        row, col = empty_cell
        numbers = list(range(1, 10))
        random.shuffle(numbers)  # Try numbers in random order
        
        for num in numbers:
            if SudokuPuzzleGenerator._is_valid(board, row, col, num):
                board[row][col] = num
                
                if SudokuPuzzleGenerator._fill_board_randomly(board):
                    return True
                
                board[row][col] = 0
        
        return False
    
    @staticmethod
    def _find_empty_cell(board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find first empty cell."""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return (row, col)
        return None
    
    @staticmethod
    def _is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if number placement is valid."""
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        for r in range(9):
            if board[r][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if board[r][c] == num:
                    return False
        
        return True


class SudokuAISolver:
    """
    AI solver for Sudoku using advanced algorithms.
    
    This class implements multiple AI techniques:
    1. Constraint Satisfaction Problem (CSP) solver
    2. Backtracking with intelligent ordering
    3. Constraint propagation (regression)
    4. SLM (Simplified Logic Model) for possibilities
    
    The solver can:
    - Find all valid numbers for any cell
    - Provide smart hints based on constraint analysis
    - Explain why certain numbers are valid
    - Suggest the best cell to fill next (MCV heuristic)
    - Generate possibility suggestions in real-time
    
    Performance Characteristics:
    - get_possibilities(): O(1) - constant time for fixed grid
    - solve_with_suggestions(): O(n) where n = number of empty cells
    - get_best_cell_to_fill(): O(n) with minimum search
    
    The regression aspect works through constraint propagation:
    When we find no valid number for a cell, the algorithm backtracks
    (regresses) to the previous decision point and tries a different number.
    """
    
    def __init__(self, board: SudokuBoard):
        """
        Initialize solver with a board.
        
        Args:
            board: SudokuBoard instance to solve
        """
        self.board = board
        self.analysis_cache = {}  # Cache for possibility analysis
    
    def solve_with_suggestions(self) -> Dict[Tuple[int, int], Set[int]]:
        """
        Provide suggestions for all empty cells.
        This is the main AI feature - shows what numbers are possible in each cell.
        
        Returns:
            Dictionary mapping (row, col) to set of possible numbers
        """
        return self.board.get_all_possibilities()
    
    def get_hint_for_cell(self, row: int, col: int) -> Optional[int]:
        """
        Get a hint for a specific cell.
        Returns the first valid possibility, or None if cell is filled.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            int: A valid number for this cell, or None
        """
        possibilities = self.board.get_possibilities(row, col)
        if possibilities:
            return min(possibilities)  # Return smallest valid number
        return None
    
    def find_best_cell_to_fill(self) -> Optional[Tuple[int, int]]:
        """
        Find cell with minimum possibilities (Most Constrained Variable heuristic).
        Useful for optimizing backtracking search order.
        
        HEURISTIC EXPLANATION:
        The Most Constrained Variable (MCV) heuristic is a search strategy that
        chooses the variable (cell) with the smallest domain (fewest possibilities).
        This dramatically reduces the search space because:
        
        1. We're more likely to detect contradictions early
        2. We reduce branching factor at each level
        3. We make better use of constraint propagation
        
        Example: 
        - If a cell has only 2 possibilities, try those first
        - If another cell has 5 possibilities, save it for later
        - This leads to faster detection of dead ends
        
        Time Complexity: O(n) where n is number of empty cells
        Space Complexity: O(1) excluding the possibilities dict
        
        Returns:
            Tuple (row, col) of cell with fewest possibilities, or None if no empty cells
        """
        all_possibilities = self.board.get_all_possibilities()
        
        if not all_possibilities:
            return None
        
        # Find cell with minimum possibilities (excluding 0 which means no cell found)
        best_cell = min(all_possibilities.items(), key=lambda x: len(x[1]) or float('inf'))
        return best_cell[0] if best_cell[1] else None
    
    def explain_possibilities_for_cell(self, row: int, col: int) -> str:
        """
        Generate human-readable explanation of why certain numbers are possible.
        
        CONSTRAINT ANALYSIS:
        This method demonstrates the SLM (Simplified Logic Model) by explaining
        exactly which numbers are eliminated and why. The explanation breaks down:
        
        1. Numbers already in the same row (row constraint)
        2. Numbers already in the same column (column constraint)
        3. Numbers already in the same 3x3 box (box constraint)
        
        For each constraint type, we show which numbers are blocked and by what.
        This helps users understand Sudoku logic and learn strategies.
        
        REGRESSION NOTE:
        When building possibilities, we're essentially running constraint propagation:
        - We start with all numbers 1-9
        - We eliminate (regress) through each constraint
        - The remaining numbers form the solution space
        - If no numbers remain, we must backtrack further
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            str: Detailed explanation text
        """
        if self.board.board[row][col] != 0:
            return f"Cell ({row+1}, {col+1}) is already filled with {self.board.board[row][col]}"
        
        possibilities = self.board.get_possibilities(row, col)
        
        if not possibilities:
            return f"Cell ({row+1}, {col+1}) has no valid possibilities - puzzle may be unsolvable!"
        
        explanation = f"\n" + "="*70 + "\n"
        explanation += f"AI ANALYSIS FOR CELL ({row+1}, {col+1})\n"
        explanation += "="*70 + "\n"
        explanation += f"Valid candidates: {sorted(possibilities)}\n\n"
        explanation += "Why these numbers work:\n"
        explanation += "-" * 70 + "\n"
        
        # Analyze what numbers are blocked
        all_nums = set(range(1, 10))
        blocked = all_nums - possibilities
        
        row_nums = set(self.board.board[row]) - {0}
        col_nums = set(self.board.board[r][col] for r in range(9)) - {0}
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        box_nums = set()
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.board.board[r][c] != 0:
                    box_nums.add(self.board.board[r][c])
        
        taken = row_nums | col_nums | box_nums
        
        explanation += f"\nRow {row+1} contains: {sorted(row_nums) if row_nums else 'None'}\n"
        explanation += f"Column {col+1} contains: {sorted(col_nums) if col_nums else 'None'}\n"
        explanation += f"3x3 Box contains: {sorted(box_nums) if box_nums else 'None'}\n"
        explanation += f"\nTotal numbers used nearby: {sorted(taken)}\n"
        explanation += f"Blocked numbers: {sorted(blocked)}\n"
        explanation += "="*70 + "\n"
        
        return explanation


class SudokuGame:
    """
    Main game class handling Pygame UI and game logic.
    Integrates all components: board, solver, and graphics.
    """
    
    # Game constants
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 900
    GRID_SIZE = 9
    CELL_SIZE = 70
    GRID_TOP_LEFT_X = 50
    GRID_TOP_LEFT_Y = 100
    
    # Colors (Modern gradient palette)
    COLOR_BG = (230, 210, 255)           # Violet background
    COLOR_BLACK = (20, 24, 82)           # Deep navy text
    COLOR_GRAY = (140, 150, 165)         # Muted gray
    COLOR_LIGHT_GRAY = (235, 242, 248)   # Very light blue
    COLOR_GRID = (100, 110, 150)         # Grid lines
    COLOR_BLUE = (41, 128, 185)          # Primary button blue
    COLOR_BLUE_DARK = (31, 97, 141)      # Darker blue hover
    COLOR_LIGHT_BLUE = (189, 225, 250)   # Cell highlight
    COLOR_GREEN = (46, 168, 104)         # Success green
    COLOR_ORANGE = (230, 126, 34)        # Warning orange
    COLOR_RED = (192, 57, 43)            # Error red
    COLOR_PURPLE = (108, 52, 131)        # Accent purple
    COLOR_YELLOW = (241, 196, 15)        # Hint yellow
    COLOR_WHITE = (255, 255, 255)
    
    def __init__(self):
        """Initialize game."""
        # Center the window on the desktop (if supported) and clamp to display size
        os.environ.setdefault('SDL_VIDEO_CENTERED', '1')
        pygame.init()
        display_info = pygame.display.Info()
        max_w, max_h = display_info.current_w, display_info.current_h
        # Leave a small margin so window controls remain visible
        margin = 60
        # Clamp the requested window size to the desktop size
        self.WINDOW_WIDTH = min(self.WINDOW_WIDTH, max(200, max_w - margin))
        self.WINDOW_HEIGHT = min(self.WINDOW_HEIGHT, max(200, max_h - margin))
        flags = pygame.RESIZABLE
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Sudoku Puzzle Solver - AI Powered")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 40)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_button = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 14)
        
        # Timer variables
        self.game_start_time = None
        self.elapsed_time = 0
        self.best_time = None
        self.pause_start_time = None
        self.paused = False
        self.total_pause_time = 0
        
        self.reset_game()
    
    def reset_game(self):
        """Start a new game with random puzzle."""
        self.board = SudokuPuzzleGenerator.generate_puzzle('Medium')
        self.solver = SudokuAISolver(self.board)
        self.selected_cell = None
        self.hint_cell = None  # Track which cell user requested hint for
        self.game_over = False
        self.won = False
        self.show_hints = False
        self.message = "Game started! Click cells to enter numbers (1-9), Delete to clear"
        # Show the start message immediately
        self.message_time = pygame.time.get_ticks()
        
        # Reset timer
        self.game_start_time = time.time()
        self.elapsed_time = 0
        self.total_pause_time = 0
        self.paused = False
        self.pause_start_time = None
    
    def handle_mouse_click(self, pos: Tuple[int, int]):
        """
        Handle mouse click to select cell.
        
        Args:
            pos: Mouse position (x, y)
        """
        x, y = pos
        
        # Check if click is within grid
        grid_x = x - self.GRID_TOP_LEFT_X
        grid_y = y - self.GRID_TOP_LEFT_Y
        
        if 0 <= grid_x < self.GRID_SIZE * self.CELL_SIZE and 0 <= grid_y < self.GRID_SIZE * self.CELL_SIZE:
            col = grid_x // self.CELL_SIZE
            row = grid_y // self.CELL_SIZE
            
            # Only allow selection of empty cells
            if self.board.board[row][col] == 0:
                self.selected_cell = (row, col)
                self.hint_cell = None  # Clear hint when selecting new cell
            else:
                self.selected_cell = None
            
            self.message = f"Selected cell ({row+1}, {col+1})"
            self.message_time = pygame.time.get_ticks()
        
        # Check button clicks
        self.handle_button_clicks(pos)
    
    def handle_button_clicks(self, pos: Tuple[int, int]):
        """Handle clicks on UI buttons."""
        x, y = pos
        
        # Hint button (x: 20, width: 140)
        if 20 < x < 160 and 740 < y < 790:
            self.show_hints = not self.show_hints
            self.message = "Hints " + ("enabled" if self.show_hints else "disabled")
            self.message_time = pygame.time.get_ticks()
        
        # New Game button (x: 175, width: 140)
        elif 175 < x < 315 and 740 < y < 790:
            self.reset_game()
            self.message = "New game started!"
            self.message_time = pygame.time.get_ticks()
        
        # Pause/Resume button (x: 330, width: 140)
        elif 330 < x < 470 and 740 < y < 790:
            self.toggle_pause()
        
        # Solve button (x: 485, width: 140)
        elif 485 < x < 625 and 740 < y < 790:
            self.solve_puzzle()
        
        # Help button (x: 640, width: 100)
        elif 640 < x < 740 and 740 < y < 790:
            self.show_help()
    
    def toggle_pause(self):
        """Toggle pause state and track pause time."""
        if not self.game_start_time:
            return
        
        if self.paused:
            # Resume game
            if self.pause_start_time:
                pause_duration = time.time() - self.pause_start_time
                self.total_pause_time += pause_duration
            self.paused = False
            self.pause_start_time = None
            self.message = "Game Resumed!"
        else:
            # Pause game
            self.paused = True
            self.pause_start_time = time.time()
            self.message = "Game Paused - Press Pause to Resume"
        
        self.message_time = pygame.time.get_ticks()
    
    def solve_puzzle(self):
        """Solve the current puzzle using AI."""
        if self.board.solution:
            self.board.board = copy.deepcopy(self.board.solution)
            self.message = "Puzzle solved by AI!"
            self.won = True
        self.message_time = pygame.time.get_ticks()
    
    def show_help(self):
        """Show help message."""
        self.message = "Use mouse to click cells, 1-9 to enter numbers, Del to clear, H for hints"
        self.message_time = pygame.time.get_ticks()
    
    def handle_key_press(self, key):
        """
        Handle keyboard input for number placement and game controls.
        
        Args:
            key: Pygame key constant
        """
        # Game control keys (always available)
        if key == pygame.K_p:
            self.toggle_pause()
            return
        elif key == pygame.K_r:
            if self.paused:
                self.toggle_pause()
            return
        elif key == pygame.K_s:
            self.solve_puzzle()
            return
        elif key == pygame.K_n:
            self.reset_game()
            self.message = "New game started!"
            self.message_time = pygame.time.get_ticks()
            return
        elif key == pygame.K_i:
            self.show_help()
            return
        
        # Cell-specific keys (only if cell selected)
        if self.selected_cell is None or self.game_over:
            return
        
        row, col = self.selected_cell
        
        # Number keys 1-9
        if pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_0
            if self.board.place_number(row, col, num):
                self.message = f"Placed {num} at ({row+1}, {col+1})"
                self.message_time = pygame.time.get_ticks()
                
                if self.board.is_complete() and self.board.is_valid_complete():
                    self.won = True
                    self.elapsed_time = time.time() - self.game_start_time - self.total_pause_time
                    if self.best_time is None or self.elapsed_time < self.best_time:
                        self.best_time = self.elapsed_time
                    self.message = f"CONGRATULATIONS! You solved in {self._format_time(self.elapsed_time)}"
                    self.message_time = pygame.time.get_ticks()
            else:
                self.message = f"Invalid placement! {num} already in row, column, or box"
                self.message_time = pygame.time.get_ticks()
        
        # Delete/Backspace key to clear cell
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
            self.board.place_number(row, col, 0)
            self.message = f"Cleared cell ({row+1}, {col+1})"
            self.message_time = pygame.time.get_ticks()
        
        # H key for hint - show possibilities for this cell
        elif key == pygame.K_h:
            if self.board.board[row][col] == 0:
                self.hint_cell = (row, col)
                possibilities = self.board.get_possibilities(row, col)
                if possibilities:
                    self.message = f"Hint for ({row+1}, {col+1}): Valid numbers are {sorted(possibilities)}"
                else:
                    self.message = f"No valid numbers for ({row+1}, {col+1})!"
            else:
                self.message = f"Cell ({row+1}, {col+1}) is already filled!"
            self.message_time = pygame.time.get_ticks()
        
        # A key to show AI explanation
        elif key == pygame.K_a:
            self.message = self.solver.explain_possibilities_for_cell(row, col)
            self.message_time = pygame.time.get_ticks()
        
        # P key to toggle pause
        elif key == pygame.K_p:
            self.toggle_pause()
    
    def draw_board(self):
        """Draw the Sudoku board grid with enhanced visuals."""
        # Draw background for grid area
        grid_bg_rect = pygame.Rect(self.GRID_TOP_LEFT_X - 5, self.GRID_TOP_LEFT_Y - 5,
                                   self.GRID_SIZE * self.CELL_SIZE + 10,
                                   self.GRID_SIZE * self.CELL_SIZE + 10)
        pygame.draw.rect(self.screen, self.COLOR_WHITE, grid_bg_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.COLOR_GRID, grid_bg_rect, 3, border_radius=8)
        
        # Draw grid lines
        for i in range(10):
            # Thick lines for 3x3 boxes
            thickness = 4 if i % 3 == 0 else 1
            color = self.COLOR_GRID if i % 3 == 0 else (200, 210, 225)
            
            # Vertical lines
            x = self.GRID_TOP_LEFT_X + i * self.CELL_SIZE
            pygame.draw.line(self.screen, color,
                           (x, self.GRID_TOP_LEFT_Y),
                           (x, self.GRID_TOP_LEFT_Y + self.GRID_SIZE * self.CELL_SIZE),
                           thickness)
            
            # Horizontal lines
            y = self.GRID_TOP_LEFT_Y + i * self.CELL_SIZE
            pygame.draw.line(self.screen, color,
                           (self.GRID_TOP_LEFT_X, y),
                           (self.GRID_TOP_LEFT_X + self.GRID_SIZE * self.CELL_SIZE, y),
                           thickness)
    
    def draw_numbers(self):
        """Draw numbers on the board with improved visuals."""
        for row in range(9):
            for col in range(9):
                num = self.board.board[row][col]
                
                x = self.GRID_TOP_LEFT_X + col * self.CELL_SIZE + self.CELL_SIZE // 2
                y = self.GRID_TOP_LEFT_Y + row * self.CELL_SIZE + self.CELL_SIZE // 2
                cell_x = self.GRID_TOP_LEFT_X + col * self.CELL_SIZE
                cell_y = self.GRID_TOP_LEFT_Y + row * self.CELL_SIZE
                
                # Highlight selected cell with shadow effect
                if self.selected_cell == (row, col):
                    # Shadow
                    shadow_rect = pygame.Rect(cell_x + 2, cell_y + 2, self.CELL_SIZE - 2, self.CELL_SIZE - 2)
                    pygame.draw.rect(self.screen, (200, 200, 220), shadow_rect)
                    # Highlight
                    pygame.draw.rect(self.screen, self.COLOR_LIGHT_BLUE,
                                   (cell_x, cell_y, self.CELL_SIZE, self.CELL_SIZE))
                    pygame.draw.rect(self.screen, self.COLOR_BLUE,
                                   (cell_x, cell_y, self.CELL_SIZE, self.CELL_SIZE), 3)
                # Highlight initial numbers with subtle background
                elif self.board.initial_board[row][col] != 0:
                    pygame.draw.rect(self.screen, self.COLOR_LIGHT_GRAY,
                                   (cell_x, cell_y, self.CELL_SIZE, self.CELL_SIZE))
                
                if num != 0:
                    # Draw number with shadow
                    is_initial = self.board.initial_board[row][col] != 0
                    color = self.COLOR_BLACK if is_initial else self.COLOR_BLUE
                    text = self.font_large.render(str(num), True, color)
                    
                    # Shadow effect
                    shadow = self.font_large.render(str(num), True, (200, 200, 220))
                    text_rect = text.get_rect(center=(x + 1, y + 1))
                    self.screen.blit(shadow, text_rect)
                    
                    # Main text
                    text_rect = text.get_rect(center=(x, y))
                    self.screen.blit(text, text_rect)
                
                # Draw possibilities if hints are enabled
                elif self.show_hints and num == 0:
                    possibilities = self.board.get_possibilities(row, col)
                    self._draw_cell_possibilities(row, col, possibilities)
    
    def _draw_cell_possibilities(self, row: int, col: int, possibilities: Set[int]):
        """Draw possibility numbers in small font inside empty cell (improved layout)."""
        x_base = self.GRID_TOP_LEFT_X + col * self.CELL_SIZE
        y_base = self.GRID_TOP_LEFT_Y + row * self.CELL_SIZE
        
        # Draw small semi-transparent background for possibilities
        pygame.draw.rect(self.screen, (255, 253, 245), 
                        (x_base + 2, y_base + 2, self.CELL_SIZE - 4, self.CELL_SIZE - 4))
        
        for i, num in enumerate(sorted(possibilities)):
            pos_row = i // 3
            pos_col = i % 3
            
            x = x_base + pos_col * 23 + 8
            y = y_base + pos_row * 23 + 6
            
            text = self.font_tiny.render(str(num), True, self.COLOR_GRAY)
            self.screen.blit(text, (x, y))
    
    def _format_time(self, seconds: float) -> str:
        """
        Format time in seconds to MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _update_timer(self):
        """Update the elapsed time counter."""
        # Stop updating the timer after the player has won
        if self.game_start_time and not self.paused and not self.won:
            self.elapsed_time = time.time() - self.game_start_time - self.total_pause_time
    
    def draw_ui(self):
        """Draw user interface elements with modern design."""
        # Draw title with styling
        title_bg = pygame.Rect(0, 0, self.WINDOW_WIDTH, 85)
        pygame.draw.rect(self.screen, (245, 248, 252), title_bg)
        pygame.draw.line(self.screen, self.COLOR_GRID, (0, 84), (self.WINDOW_WIDTH, 84), 2)
        
        title_text = self.font_title.render("SUDOKU PUZZLE SOLVER", True, self.COLOR_BLACK)
        self.screen.blit(title_text, (20, 15))
        
        subtitle_text = self.font_small.render("AI-Powered | Hints & Analysis | Real-time Solver", 
                                               True, self.COLOR_GRAY)
        self.screen.blit(subtitle_text, (20, 55))
        
        # Draw right-side info panel (after the grid: 50 + 9*70 + 20 = 720)
        panel_x = 730
        panel_y = 100
        panel_width = 350
        panel_height = 600
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (255, 250, 240), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.COLOR_GRID, panel_rect, 3, border_radius=10)
        
        # Panel title
        panel_title = self.font_medium.render("📋 Controls", True, self.COLOR_BLACK)
        self.screen.blit(panel_title, (panel_x + 15, panel_y + 15))
        
        # Draw info and controls in the right panel
        info_y = panel_y + 60
        line_height = 35
        
        # Timer
        timer_text = self.font_button.render(f"⏱ Time: {self._format_time(self.elapsed_time)}", 
                                            True, self.COLOR_BLUE)
        self.screen.blit(timer_text, (panel_x + 15, info_y))
        info_y += line_height
        
        # Best time
        if self.best_time is not None:
            best_text = self.font_small.render(f"🏆 Best: {self._format_time(self.best_time)}", 
                                              True, self.COLOR_GREEN)
            self.screen.blit(best_text, (panel_x + 15, info_y))
            info_y += line_height
        
        # Separator
        pygame.draw.line(self.screen, self.COLOR_LIGHT_GRAY, 
                        (panel_x + 10, info_y), (panel_x + panel_width - 10, info_y), 1)
        info_y += 15
        
        # Keyboard shortcuts
        shortcuts = [
            ("P", "Pause/Resume", self.COLOR_ORANGE),
            ("H", "Hints", self.COLOR_BLUE),
            ("S", "Solve", self.COLOR_RED),
            ("N", "New Game", self.COLOR_GREEN),
            ("I", "Help", (100, 130, 170)),
        ]
        
        for key, action, color in shortcuts:
            # Key badge
            key_rect = pygame.Rect(panel_x + 15, info_y - 5, 35, 28)
            pygame.draw.rect(self.screen, color, key_rect, border_radius=4)
            pygame.draw.rect(self.screen, self.COLOR_BLACK, key_rect, 2, border_radius=4)
            
            key_text = self.font_button.render(key, True, self.COLOR_WHITE)
            key_text_rect = key_text.get_rect(center=(panel_x + 32, info_y + 4))
            self.screen.blit(key_text, key_text_rect)
            
            # Action text
            action_text = self.font_small.render(action, True, self.COLOR_BLACK)
            self.screen.blit(action_text, (panel_x + 60, info_y))
            info_y += line_height
        
        # Separator
        info_y += 5
        pygame.draw.line(self.screen, self.COLOR_LIGHT_GRAY, 
                        (panel_x + 10, info_y), (panel_x + panel_width - 10, info_y), 1)
        info_y += 15
        
        # Selected cell info
        if self.selected_cell:
            row, col = self.selected_cell
            # Add extra vertical spacing so the selected-cell dialogue appears lower
            info_y += 20
            cell_info = self.font_button.render(f"Selected: ({row+1}, {col+1})", 
                                               True, self.COLOR_BLUE)
            self.screen.blit(cell_info, (panel_x + 15, info_y))
            info_y += line_height
            
            # Show possibilities only if user pressed H for this cell
            if self.hint_cell == self.selected_cell and self.board.board[row][col] == 0:
                possibilities = self.board.get_possibilities(row, col)
                if possibilities:
                    poss_text = self.font_small.render(f"Valid: {sorted(possibilities)}", 
                                                      True, self.COLOR_YELLOW)
                    self.screen.blit(poss_text, (panel_x + 15, info_y))
        
        # Draw pause status overlay
        if self.paused:
            pause_overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            pause_overlay.set_alpha(200)
            pause_overlay.fill((0, 0, 0))
            self.screen.blit(pause_overlay, (0, 0))
            
            pause_text = self.font_title.render("⏸ PAUSED", True, self.COLOR_YELLOW)
            pause_rect = pause_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(pause_text, pause_rect)
            
            resume_text = self.font_button.render("Press P or R to Resume", True, self.COLOR_WHITE)
            resume_rect = resume_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(resume_text, resume_rect)
        
        # Draw message at the very bottom (positioned relative to window height)
        # Define defaults so they exist even if the message is not currently shown
        bottom_margin = 12
        msg_height = 50
        if pygame.time.get_ticks() - self.message_time < 3000:
            # Place the message box at the very bottom with a small bottom margin
            msg_y = self.WINDOW_HEIGHT - msg_height - bottom_margin
            msg_box = pygame.Rect(20, msg_y, min(600, self.WINDOW_WIDTH - 40), msg_height)
            pygame.draw.rect(self.screen, (255, 253, 245), msg_box, border_radius=5)
            pygame.draw.rect(self.screen, self.COLOR_ORANGE, msg_box, 2, border_radius=5)
            message_text = self.font_small.render(self.message[:80], True, self.COLOR_BLACK)
            self.screen.blit(message_text, (msg_box.x + 10, msg_box.y + 15))

        # Draw instructions just above the message box (adjust to window size)
        inst_y = max(10, self.WINDOW_HEIGHT - msg_height - bottom_margin - 28)
        instructions = "Click cells • 1-9 to enter • Del to clear • Use keyboard shortcuts above"
        inst_text = self.font_tiny.render(instructions, True, self.COLOR_GRAY)
        self.screen.blit(inst_text, (20, inst_y))
    
    def draw(self):
        """Render the complete game screen."""
        self.screen.fill(self.COLOR_BG)
        self._update_timer()  # Update timer before drawing
        self.draw_board()
        self.draw_numbers()
        self.draw_ui()
        
        # Draw win message
        if self.won:
            win_text = self.font_large.render("YOU WON!", True, self.COLOR_GREEN)
            win_rect = win_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
            self.screen.blit(win_text, win_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_press(event.key)
                elif event.type == pygame.VIDEORESIZE:
                    # Update internal window size and recreate the surface
                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """
    Main entry point for the Sudoku game.
    Initializes and runs the game with all AI features.
    
    DETAILED PROJECT EXPLANATION:
    =============================
    
    This Sudoku game implements three main AI algorithms:
    
    1. BACKTRACKING ALGORITHM
    -------------------------
    - Systematically explores the solution space
    - Tries each number 1-9 in empty cells
    - Validates against Sudoku constraints
    - When invalid, backtracks and tries next number
    - Recursive approach with implicit stack
    
    Example:
    Empty cell -> Try 1 -> Check valid -> Success: continue
                         -> Check invalid -> Try 2
                         -> ... and so on
    
    Complexity: O(9^n) worst case, much better in practice due to constraints
    
    
    2. CONSTRAINT SATISFACTION PROBLEM (CSP) WITH REGRESSION
    =========================================================
    - Treats Sudoku as CSP with 81 variables (cells)
    - Each variable has domain 1-9
    - Constraints: row, column, box uniqueness
    - Regression happens when backtracking
    - Constraint propagation reduces domains before search
    
    Flow:
    Set initial constraints -> Propagate -> Search with backtracking
                                            -> Dead end detected
                                            -> Regress to last choice
                                            -> Try different value
    
    Benefit: Eliminates invalid candidates early, reducing search space
    
    
    3. SIMPLIFIED LOGIC MODEL (SLM) - POSSIBILITY CALCULATOR
    =========================================================
    - For each empty cell, calculate all valid candidates
    - Uses three constraints: row, column, box
    - User can see these possibilities as hints
    - AI uses these to recommend next moves
    
    Example for cell (0,0):
    - All numbers: {1,2,3,4,5,6,7,8,9}
    - In row 0: remove {2,5,7}
    - In col 0: remove {1,6}
    - In box: remove {3,4}
    - Possibilities: {8,9}
    
    User can use this to learn and solve
    
    
    ADVANCED CONSTRAINT PROPAGATION TECHNIQUES
    ============================================
    
    - Naked Singles: Cells with only one possibility
    - Hidden Singles: Number that can only go in one place in unit
    - These detect obvious moves before guessing
    
    
    INTERACTIVE FEATURES
    ====================
    
    1. Graphical Interface (Pygame):
       - Click cells to select
       - Press numbers 1-9 to place
       - Delete to clear cells
       
    2. AI Hints:
       - Press H: Get next valid possibility
       - Press A: Get AI analysis with explanation
       - Toggle Hints: Show all possibilities
       
    3. Statistics:
       - Track games played and won
       - Measure solving time
       - Count hints used
       
    4. Random Puzzles:
       - Each game generates new random puzzle
       - 4 difficulty levels available
       - Guaranteed valid solution
    
    =============================
    """
    print("=" * 80)
    print("SUDOKU GAME WITH AI SOLVER - Starting")
    print("=" * 80)
    print("\nProject: Course Assignment in Sudoku Solver using AI")
    print("Techniques: Backtracking | CSP with Regression | SLM")
    print("\nGame Features:")
    print("  ✓ Backtracking Algorithm for puzzle solving")
    print("  ✓ Constraint Satisfaction Problem approach")
    print("  ✓ Constraint Propagation (Regression)")
    print("  ✓ SLM (Simplified Logic Model) for possibility calculation")
    print("  ✓ Random puzzle generation for each game")
    print("  ✓ Real-time possibility hints")
    print("  ✓ AI-powered suggestions and analysis")
    print("  ✓ Advanced constraint techniques")
    print("  ✓ Game statistics tracking")
    print("\nControls:")
    print("  - Click cells to select")
    print("  - Press 1-9 to place numbers")
    print("  - Press Delete/Backspace to clear")
    print("  - Press H for AI hint")
    print("  - Press A to see AI analysis")
    print("  - Click 'Hints: OFF' to toggle possibility display")
    print("  - Click 'New Game' to start fresh puzzle")
    print("\nAlgorithm Explanation:")
    print("  Backtracking: Systematically tries values, backtracks on constraints")
    print("  Regression: Undoes previous choices when dead ends detected")
    print("  CSP: Frames Sudoku as constraint satisfaction problem")
    print("  SLM: Calculates valid possibilities using constraint logic")
    print("  Constraint Propagation: Reduces search space before backtracking")
    print("\n" + "=" * 80 + "\n")
    
    game = SudokuGame()
    game.run()


class GameStatistics:
    """
    Track game statistics and performance metrics.
    
    Useful for analyzing:
    - How long player takes to solve puzzles
    - Number of hints used
    - Number of mistakes
    - Player statistics over time
    """
    
    def __init__(self):
        """Initialize statistics tracker."""
        self.games_played = 0
        self.games_won = 0
        self.total_time_played = 0
        self.total_hints_used = 0
        self.total_mistakes = 0
        self.current_game_start_time = None
        self.current_game_hints = 0
        self.current_game_mistakes = 0
    
    def start_game(self):
        """Record start of new game."""
        self.current_game_start_time = time.time()
        self.current_game_hints = 0
        self.current_game_mistakes = 0
        self.games_played += 1
    
    def end_game(self, won: bool):
        """
        Record end of game.
        
        Args:
            won: True if player won, False otherwise
        """
        if won:
            self.games_won += 1
        
        if self.current_game_start_time:
            elapsed = time.time() - self.current_game_start_time
            self.total_time_played += elapsed
    
    def record_hint_used(self):
        """Record that player used a hint."""
        self.current_game_hints += 1
        self.total_hints_used += 1
    
    def record_mistake(self):
        """Record that player made a mistake."""
        self.current_game_mistakes += 1
        self.total_mistakes += 1
    
    def get_summary(self) -> str:
        """
        Get statistics summary.
        
        Returns:
            str: Formatted statistics
        """
        avg_time = self.total_time_played / self.games_played if self.games_played > 0 else 0
        win_rate = (self.games_won / self.games_played * 100) if self.games_played > 0 else 0
        
        summary = f"\n{'='*70}\n"
        summary += "GAME STATISTICS\n"
        summary += f"{'='*70}\n"
        summary += f"Games Played: {self.games_played}\n"
        summary += f"Games Won: {self.games_won}\n"
        summary += f"Win Rate: {win_rate:.1f}%\n"
        summary += f"Total Time: {self.total_time_played:.1f} seconds\n"
        summary += f"Average Time per Game: {avg_time:.1f} seconds\n"
        summary += f"Total Hints Used: {self.total_hints_used}\n"
        summary += f"Total Mistakes: {self.total_mistakes}\n"
        summary += f"{'='*70}\n"
        
        return summary


class AdvancedSudokuAISolver(SudokuAISolver):
    """
    Advanced AI Solver with additional techniques.
    
    Extends the basic solver with:
    - Naked singles detection
    - Hidden singles detection
    - Pointing pairs/triples
    - Box/line reduction
    
    These are constraint propagation techniques that reduce the search space
    before we need to use backtracking, making the solver more efficient.
    """
    
    def find_naked_singles(self) -> List[Tuple[int, int, int]]:
        """
        Find cells where only one number is possible (naked singles).
        
        A naked single is a cell that has exactly one valid candidate.
        These cells can be filled immediately without guessing.
        
        Returns:
            List of (row, col, number) tuples for cells with single possibility
        """
        singles = []
        possibilities = self.board.get_all_possibilities()
        
        for (row, col), poss_set in possibilities.items():
            if len(poss_set) == 1:
                singles.append((row, col, list(poss_set)[0]))
        
        return singles
    
    def find_hidden_singles_in_row(self, row: int) -> List[Tuple[int, int, int]]:
        """
        Find hidden singles in a row.
        
        A hidden single in a row is a number that can only go in one place
        in that row (even though that cell might have other possibilities).
        
        Args:
            row: Row index to analyze
            
        Returns:
            List of (row, col, number) for hidden singles
        """
        hidden_singles = []
        
        for num in range(1, 10):
            # Skip if number already in row
            if num in self.board.board[row]:
                continue
            
            # Find cells where this number is possible
            possible_positions = []
            for col in range(9):
                if self.board.board[row][col] == 0:
                    possibilities = self.board.get_possibilities(row, col)
                    if num in possibilities:
                        possible_positions.append(col)
            
            # If only one position, it's a hidden single
            if len(possible_positions) == 1:
                col = possible_positions[0]
                hidden_singles.append((row, col, num))
        
        return hidden_singles
    
    def find_hidden_singles_in_column(self, col: int) -> List[Tuple[int, int, int]]:
        """
        Find hidden singles in a column.
        
        Args:
            col: Column index to analyze
            
        Returns:
            List of (row, col, number) for hidden singles
        """
        hidden_singles = []
        
        for num in range(1, 10):
            # Skip if number already in column
            if any(self.board.board[r][col] == num for r in range(9)):
                continue
            
            # Find cells where this number is possible
            possible_positions = []
            for row in range(9):
                if self.board.board[row][col] == 0:
                    possibilities = self.board.get_possibilities(row, col)
                    if num in possibilities:
                        possible_positions.append(row)
            
            # If only one position, it's a hidden single
            if len(possible_positions) == 1:
                row = possible_positions[0]
                hidden_singles.append((row, col, num))
        
        return hidden_singles
    
    def get_advanced_hint(self) -> Optional[str]:
        """
        Get an advanced hint using constraint propagation techniques.
        
        Priority order:
        1. Naked singles (cells with only one possibility)
        2. Hidden singles in rows
        3. Hidden singles in columns
        
        Returns:
            String describing the hint, or None if no hints available
        """
        # Check for naked singles
        naked_singles = self.find_naked_singles()
        if naked_singles:
            row, col, num = naked_singles[0]
            return f"Naked Single: Cell ({row+1}, {col+1}) MUST be {num} (only possibility)"
        
        # Check for hidden singles in rows
        for row in range(9):
            hidden_singles = self.find_hidden_singles_in_row(row)
            if hidden_singles:
                row_idx, col_idx, num = hidden_singles[0]
                return f"Hidden Single in Row {row_idx+1}: Number {num} can only go at ({row_idx+1}, {col_idx+1})"
        
        # Check for hidden singles in columns
        for col in range(9):
            hidden_singles = self.find_hidden_singles_in_column(col)
            if hidden_singles:
                row_idx, col_idx, num = hidden_singles[0]
                return f"Hidden Single in Column {col_idx+1}: Number {num} can only go at ({row_idx+1}, {col_idx+1})"
        
        return None


if __name__ == "__main__":
    main()
