# Import libraries
import matplotlib.pyplot as plt
import numpy as np 
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from IPython.display import Image, clear_output, display
from io import BytesIO # For temporary image storage

"""
This class solves N-Queens with backtracking algorithm and Arc Consistency (AC). 
The Solver will work through the chessboard row by row. Arc Consistency will 
hypothetically place a Queen in each safe spot in the current row and check 
whether all remaining rows have at least one safe spot. If not, then that safe 
spot is longer safe and pruned off from the domain. Arc Consistency encourages 
early detection of failures and shrinks down the search state space size by 
looking ahead to prune off unsafe cols in each row (most effective when combined 
with ordering strategies; could be computationally expensive).
"""
class N_Queens_Solver_AC:
    """
    This function initializes class parameters for N-Queens Solver.
    """
    def __init__(self, img_output_area, progress_bar, progress_label, vis, 
                 num_img, size=8):
        self.n = size # Board size
        self.board = [[0] * self.n for _ in range(self.n)] # Board as 2D Grid
        self.threats = [[0] * self.n for _ in range(self.n)] # threats tracker
        self.positions = [] # Queen placement positions
        self.step_number = 0 # Track number of steps
        self.queen_placement = 0 # Track number of queen_placement steps
        self.backtracking = 0 # Track number of backtracking steps
        self.figures = [] # Store image steps for visualizations 
        self.output_area = img_output_area # Initialize output area for image
        self.vis = vis #  Boolean control for generating visualization 
        self.progress_bar = progress_bar # Initialize progress bar 
        self.progress_label = progress_label # Initialize progress label
        self.num_img = num_img # Initialize total number of image steps required
        self.progress = 0 # Track image steps generation 

    """
    This function updates threats value for a spot given row and column.
    """
    def update_threats(self, threats, row, col):
        # Update current spot
        threats[row][col] += 1

        # Update same row; skip current spot
        for i in range(row): 
            threats[i][col] += 1
        for i in range(row + 1, self.n): 
            threats[i][col] += 1

        # Update same col; skip current spot
        for j in range(col): 
            threats[row][j] += 1
        for j in range(col + 1, self.n): 
            threats[row][j] += 1

        # Update lower left diagonal
        for i, j in zip(range(row + 1, self.n), range(col - 1, -1, -1)):
            threats[i][j] += 1

        # Update lower right diagonal
        for i, j in zip(range(row + 1, self.n), range(col + 1, self.n)):
            threats[i][j] += 1

        # Update upper left diagonal
        for i, j in zip(range(row - 1, -1, -1), range(col - 1, -1, -1)):
            threats[i][j] += 1
        
        # Update upper right diagonal
        for i, j in zip(range(row - 1, -1, -1), range(col + 1, self.n, 1)):
            threats[i][j] += 1

    """
    This function backtracks threats value for a spot given row and column.
    """
    def backtrack_threats(self, threats, row, col):
        # Update current spot
        threats[row][col] -= 1

        # Update same row; skip current spot
        for i in range(row): 
            threats[i][col] -= 1
        for i in range(row + 1, self.n): 
            threats[i][col] -= 1

        # Update same col; skip current spot
        for j in range(col): 
            threats[row][j] -= 1
        for j in range(col + 1, self.n): 
            threats[row][j] -= 1

        # Update lower left diagonal
        for i, j in zip(range(row + 1, self.n), range(col - 1, -1, -1)):
            threats[i][j] -= 1

        # Update lower right diagonal
        for i, j in zip(range(row + 1, self.n), range(col + 1, self.n)):
            threats[i][j] -= 1

        # Update upper left diagonal
        for i, j in zip(range(row - 1, -1, -1), range(col - 1, -1, -1)):
            threats[i][j] -= 1
        
        # Update upper right diagonal
        for i, j in zip(range(row - 1, -1, -1), range(col + 1, self.n, 1)):
            threats[i][j] -= 1

    """
    This function checks whether a given row has at least one safe spot.
    """
    def look_ahead(self, threats, row):
        safe = False # Boolean flag
        for j in range(self.n): 
            if threats[row][j] == 0: # Safe spot
                safe = True
                break
        return safe
    
    """
    This function returns a list of safe columns that are pruned off for the 
    given row. If a safe spot has any unoccupied rows with no remaining safe 
    spots after hypothetical Queen placement, then this coluumn is pruned off. 
    """
    def arc_consistency(self, row):
        prune = [] # List to store pruned columns for a given row
        row_threats = self.threats[row] # Threats value for current row
        
        # Extract index of safe columns based on row threats list
        safe_cols = [index for index, 
                     threats in enumerate(row_threats) if threats == 0]
        for j in safe_cols:
            threats_copy = [row[:] for row in self.threats] # Threats copy
            # Update threats copy after hypothetical Queen placement
            self.update_threats(threats_copy, row, j) 
            for i in range(row + 1, self.n):
                # Check whether a given row is safe
                if not self.look_ahead(threats_copy, i):
                    prune.append(j) # Prune off the column if unsafe
                    break  
        return prune
 
    """
    This function creates visualizations for N-Queens Solver.
    """
    def visualize_step(self):
        fig, ax = plt.subplots(figsize=(5, 5)) # Initialize plot
        board = np.zeros((self.n, self.n)) # Initialize board structure
        board[1::2, ::2] = 1 # Dark/Green squares
        board[::2, 1::2] = 1 # Dark/Green squares
        queen_img = plt.imread("queen.png")  # Load queen image piece

        zoom_factor = 0.05 * 7 / self.n # Adjust size of queen image piece

        ax.clear() # Clear axis

        # Color the chessboard with light and dark squares
        for y in range(self.n): 
            for x in range(self.n):
                # Light squares (0): beige; Dark squares (1): green
                color = "#769656" if board[y, x] == 1 else "#eeeed2"
                ax.fill_between([x, x+1], y, y+1, 
                                color=color, 
                                edgecolor="none")
                # Write threats value for empty spots on the board 
                if (y, x) not in self.positions:
                    ax.text(x+0.5, y+0.5, str(self.threats[y][x]), 
                            fontsize=8, ha='center', va='center', color='red')
                
        # Draw the Queen image piece on the board
        for y, x in self.positions:
            img = OffsetImage(queen_img, zoom=zoom_factor)
            # Creates an annotation box for Queen placement
            ab = AnnotationBbox(img, (x+0.5, y+0.5), frameon=False, 
                                boxcoords="data", pad=0)
            ax.add_artist(ab) 

        # Set plot parameters 
        ax.set_xlim(0, self.n)
        ax.set_ylim(0, self.n)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"{self.n}-Queens (Arc Consistency)")
        ax.invert_yaxis()

        # Temperarily store image steps with io buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        self.figures.append(buffer.getvalue())
        plt.close(fig)
        buffer.close()

        # Update visualization generation progress
        self.progress += 1

        # Set threshold to only save last 20 image steps if exceeded
        total_img = 20 if self.num_img > 20 else self.num_img
       
        # Update progress bar 
        if self.progress <= self.num_img:
            self.progress_bar.value = self.progress
            percent = min(int((self.progress / total_img) * 100), 100)
            self.progress_label.value = f"{percent}% Complete"

    """
    This function displays visualizations for N-Queens Solver.
    """
    def display_figure(self, index=-1):
        if self.figures:
            with self.output_area:
                clear_output(wait=True) # Clear image output area 
                display(Image(data=self.figures[index])) # Display image buffer
    
    
    """
    This function recursively finds a solution to N-Queens. The base case is 
    when current row index is exceeds the board size. Otherwise, Queen placement 
    and Backtracking steps are repeated until the board is solved. For details 
    of the methods, please refer to the beginning of this file. 
    """
    def solve_n_queens_util(self, row=0):
        # Base Case: at bottom of a filled board
        if row >= self.n:
            return True
        
        # Find the list of safe columns to prune off
        prune = self.arc_consistency(row)     

        row_threats = self.threats[row] # Threats value for current row
        # Extract index of safe columns based on row threats list
        safe_cols = [index for index, 
                    threats in enumerate(row_threats) if threats == 0]
        
        # Try Queen placement in each safe column in this row 
        for col in safe_cols:
            if col not in prune: # Check whether a column is pruned off
                # Queen Placement 
                self.board[row][col] = 1  # Place the queen
                self.update_threats(self.threats, row, col) # Update threats 
                self.positions.append((row, col)) # Add Queen position 
                self.step_number += 1 # Update total step counter
                self.queen_placement += 1 # Update Queen placement counter
                    
                # Generate visualization if vis flag is True
                if self.vis and (self.step_number > self.num_img - 20 or 
                                self.num_img <= 20): # Save last 20 steps
                    self.visualize_step()

                # Recursively call function onto next row
                if self.solve_n_queens_util(row + 1):
                    return True
                
                # Backtracking
                self.board[row][col] = 0 # Remove the Queen
                # Backtrack threats 
                self.backtrack_threats(self.threats, row, col) 
                self.positions.pop() # Remove Queen position 
                self.step_number += 1 # Update total step counter
                self.backtracking += 1 # Update backtracking step counter
                    
                # Generate visualization if vis flag is True
                if self.vis and (self.step_number > self.num_img - 20 or 
                                self.num_img <= 20): # Save last 20 steps
                    self.visualize_step()
        
    """
    This function runs the recursive N-Queens Solver with AC. 
    """
    def solve(self):
        if self.vis:
            self.visualize_step() # Initialize empty board image 
        self.solve_n_queens_util(0)
    