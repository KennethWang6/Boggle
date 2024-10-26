# Vincent Ngo 2230951 and Kenneth Wang , 2230755
# R. Vincent , instructor
# Advanced Programming , section 2
# Final Project


# Imports
import os.path
import tkinter as tk
from random import choice

# Set global variables
file = None # file name or game if game was played
board = None # matrix of board that most recently used
board_tree = None # Boggle_Eval class of board 


# Creation of Dictionaries

def dictionary_set(file):
    """Create a dictionary with all possible words"""
    words = set() # create set for all words
    fp = open(file) # read the dictionary
    for lines in fp: # add each word to the set
        words.add(lines.strip())
    # write the set into a new file
    fp = open("yawl.py","w")
    fp.write("words = "+str(words))
    return words

def dictionary_prefix(file):
    """Create a dictionary with all possible prefixes of words"""
    pre = set() # create set for all prefixes
    fp = open(file) # read the dictionary
    word=""
    for lines in fp: # add each prefix to the set
        for i in lines.strip():
            word+=i
            pre.add(word)            
        word=""
    # write the set into a new file
    fp = open("prefixes.py","w")
    fp.write("prefixes = "+str(pre))

# check if these prefixes and words file exist
# if they do not, create with dictionary file
# if dictionary file does not exist, report missing dictionary
if not os.path.exists("yawl.py"):
    if not os.path.exists("dictionary-yawl.txt"):
        print("Dictionary text file missing.")
    else:
        print("Please wait while processing...")
        dictionary_set("dictionary-yawl.txt")
        print("yawl.py created")
        from yawl import words # Import
else:
    from yawl import words # Import
if not os.path.exists("prefixes.py"):
    if not os.path.exists("dictionary-yawl.txt"):
        print("Dictionary text file missing.")
    else:     
        print("Please wait while processing...")
        dictionary_prefix("dictionary-yawl.txt")
        print("prefixes.py created")
        from prefixes import prefixes # Import
else:
    from prefixes import prefixes # Import



## Boggle Board Evaluation

class Boggle_Eval:
    """Evaluate Boggle Board"""
    class node:
        def __init__(self, value):
            """Initiate node class"""
            self.value = value
            self.link = []
            
    def __init__(self, board):
        """Initialize Boggle_Eval"""
        self.board = board
        self.row = len(board)
        self.col = len(board[0])
        self.root = None
        self.trees = []
        self.valid_words = set()
        
        
    def init_tree(self): 
        """Initializes base of tree. Iterates through every cell in the board
        and creates tree for these cells"""
        for i in range(self.row):
            for j in range(self.col):
                self.root = self.node(self.board[i][j]) # set root as node of a position on board
                visited = set() # keep track of all visited cells to not double on a cell
                self.tree(i,j,self.root, visited, self.root.value) # make tree from root
                self.trees.append(self.root)# make list with all the roots
        return self.trees
                
    def tree(self,i,j,current, visited, prefix):
        """Creates tree for a given root"""
        directions = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]] # (NW,W,SW,N,S,NE,E,SE)
        visited.add((i,j)) # save visited cells
        for x,y in directions: # go through all directions
            i1,j1 = x+i,y+j # set new values of i and j for current cell
            if i1 >= 0 and i1 < self.row and j1 >= 0 and j1 < self.col: # check if valid cell
                if prefix in prefixes: # terminate search if prefix not found
                    if (i1,j1) not in visited: # check if cell was not already visited
                        Next = self.node(self.board[i1][j1]) # new node from i1,j1
                        current.link.append(Next) # append new node to list associated to the current root
                        self.tree(i1,j1,Next, visited, prefix+Next.value) # continue making branches with next node
        visited.remove((i,j)) # backtrack visited cells

    @staticmethod
    def verify_data(file):
        """Verifies file content is a Boggle Board"""
        fp = open(file) # 
        board = [lines.strip().split() for lines in fp]
        board_size = board[0] # first line of file which is the board size
        board_data = board[1:] # the board itself
        if len(board_size) != 2: # verifies only 2 items
            return None
        if board_size[0].isdigit() and board_size[1].isdigit(): # verifies both items are digits
            r, c = int(board_size[0]), int(board_size[1]) # save sizes
        else:
            return None
        R = len(board_data) # check number of rows in board itself
        if R != r: # verify rows in board itself and digit given for rows is the same
            return None
        for lines in range(0, len(board_data)): 
            for letter in board_data[lines]:
                if not letter.isalpha(): # verify each character in the board is a letter
                    return None
                if not letter.isupper(): # verify each letter is CAP
                    return None
            C = len(board_data[lines])
            if C != c: # verify columns in board itself and digit given for columns is the same
                return None
        return True

    @staticmethod
    def read_data(file):
        """read the Boggle files so it can be used for eval"""
        fp = open(file)
        board = [lines.strip().split() for lines in fp]
        board_size = board[0]
        board_data = board[1:]
        return board_data
    
    def read_words(self,node,word=""):
        """read all valid words in the tree
        Reconstructs words from node and value"""
        word+=node.value # Construct word letter by letter
        if word in words: # check if its in the dictionary to add words
            self.valid_words.add(word)
        for link in node.link: # go next
            self.read_words(link, word) # recursively call to add another letter
        return self.valid_words # return set of valids word
       
    @staticmethod      
    def points(word_list, points = 0):
        """Calculate the number of points awarded for given list of words"""
        for words in word_list: # award points depending on length
            l = len(words)
            # number of points awarded from wikipedia
            if l<3: continue
            elif l==3 or l==4: points+=1
            elif l==5: points+=2
            elif l==6: points+=3
            elif l==7: points+=5
            else: points+=11
        return points



## Boggle Game

class BoggleGame:
    """UI for Boggle Game"""
    
    def __init__(self, master, board_data, valid_words):
        """Initialize BoggleGame"""
        self.master = master
        self.master.title("Boggle Game")
        self.board_data = board_data
        self.valid_words = valid_words
        self.board_size = (len(board_data), len(board_data[0]))
        self.points = 0 # points for game
        # create display board
        self.board = [[None for _ in range(self.board_size[1])] for _ in range(self.board_size[0])] 
        self.create_board_widgets()
        # add submission feature and displays
        self.create_input_widgets()
        self.entered_words = set() 
        
    def create_board_widgets(self):
        """Add letters to board display"""
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                label = tk.Label(self.master, text=self.board_data[i][j], font=("Arial", 20), width=4, height=2)
                label.grid(row=i, column=j)
                self.board[i][j] = label

    def create_input_widgets(self):
        """Create submission feature & display of valid words and points"""
        # Field for word input from user
        self.word_input = tk.Entry(self.master, font=("Arial", 14))
        self.word_input.grid(row=self.board_size[0] + 1, columnspan=self.board_size[1])
        # Submit button and submit when clicks enter
        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit_word)
        self.submit_button.grid(row=self.board_size[0] + 2, columnspan=self.board_size[1])
        self.master.bind("<Return>", lambda event: self.submit_word())
        # Display of "valid words"
        self.valid_words_label = tk.Label(self.master, text="Valid Words:", font=("Arial", 12))
        self.valid_words_label.grid(row=self.board_size[0] + 3, columnspan=self.board_size[1])
        # Display of valid words entered
        self.valid_words_display = tk.Label(self.master, text="", font=("Arial", 12), wraplength=200)
        self.valid_words_display.grid(row=self.board_size[0] + 4, columnspan=self.board_size[1])
        # Display of points
        points_label = tk.Label(self.master, text="Points: {}".format(self.points), font=("Arial", 12))
        points_label.grid(row=self.board_size[0] + 5, columnspan=self.board_size[1])
        
    def submit_word(self):
        """User submits word"""
        word = self.word_input.get().upper() # get word from the field dedicated for input
        if self.is_valid_word(word): # if word is valid
            self.valid_words_display.config(text=self.valid_words_display.cget("text") + word + ", ") # update valid word list
            # update points
            self.points += Boggle_Eval.points([word]) 
            points_label = tk.Label(self.master, text="Points: {}".format(self.points), font=("Arial", 12))
            points_label.grid(row=self.board_size[0] + 5, columnspan=self.board_size[1])
        self.clear_selection() # clear field dedicated for input

    def is_valid_word(self, word):
        """Verifies if user entered word is valid"""
        if len(word) < 3: # word too short
            return False
        elif word in self.entered_words: # word already entered previously
            return False
        elif word in self.valid_words: # word is good
            self.entered_words.add(word)
            return True
        else: # any other input
            return False

    def clear_selection(self):
        """Clears input in entry box"""
        self.word_input.delete(0, tk.END)

def generate_random_board():
    """Creates a random 4 x 4 Boggle Board"""
    global file
    global board
    global board_tree
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # choice of letters
    board_size = 4  # board size 4 x 4
    board = [[choice(letters) for _ in range(board_size)] for _ in range(board_size)]
    board_tree = Boggle_Eval(board)
    trees = board_tree.init_tree() # creates all trees
    for root in trees:
        board_tree.read_words(root) # reads through trees to find valid words
    if len(board_tree.valid_words) < 200: # if possible words are too limited
        return generate_random_board() # retry
    return board, board_tree.valid_words 



## Main Programs

def file_to_board():
    """Requests Boggle Board File and Reads It"""
    global file
    global board
    global board_tree
    file = input("Enter file name: ") # input for file
    path = './'+file
    check_file = os.path.exists(path) # ensure file exists
    if not check_file: # if file does not exist
        print("Invalid file name")
        file_to_board() # retry
    else:
        valid_board = Boggle_Eval.verify_data(file) # verify file contents
        if valid_board == None: # if file format invalid
            print("File has invalid format")
            file_to_board() # retry
        else: # otherwise, all good so read the file
            board = Boggle_Eval.read_data(file)
            board_tree = Boggle_Eval(board)
            trees = board_tree.init_tree() # creates all trees
            for root in trees:
                board_tree.read_words(root) # reads through trees to find valid words

def game():
    """Runs that Boggle game"""
    global file
    global board
    global board_tree
    file = 'game'
    board_data, valid_words = generate_random_board()
    root = tk.Tk()
    boggle_game = BoggleGame(root, board_data, valid_words)
    root.mainloop()

def first_menu():
    """Initial menu"""
    global file
    global board
    global board_tree
    first_menu_str = """
Select one of the following options:
1. Enter another file name
2. Play Boggle
3. Exit
Enter your choice:"""
    option = input(first_menu_str)
    if option == "1": # reads file and then runs other menu
        file_to_board() 
        menu()
    elif option == "2": # runs game and then runs other menu
        print('game')
        game()
        menu()
    elif option == "3":
        pass
    else:
        print("Invalid option.")
        first_menu()

def menu():
    """Menu in use after a game has been played or file has been entered"""
    global file
    global board
    global board_tree
    option = 0
    menu_str = """
Select one of the following options:
1. Print valid words of {:s}
2. Print boggle table of {:s}
3. Print maximum points of {:s}
4. Enter another file name
5. Play Boggle
6. Exit
Enter your choice:"""
    while option != "6":
        option = input(menu_str.format(file, file, file))
        if option == "1": # prints valid words of previous boggle board
            print(board_tree.valid_words)
        elif option =="2": # prints previous boggle board
            print(str(board_tree.row) + "x" + str(board_tree.col))
            for row in board:
                print(" ".join(row))
        elif option == "3": # prints maximum points for previous boggle board
            print(f"Maximum points: {Boggle_Eval.points(board_tree.valid_words)}")
        elif option == "4": # reads file
            file_to_board()
        elif option == "5": # runs game
            game()
        elif option != "6": # invalid option
            print("Please enter a valid option.")



# Ensure dictionary and prefixes exist
if os.path.exists("yawl.py"):
    if os.path.exists("prefixes.py"):
        first_menu() # Run the first menu

       


