
"""

    Sokoban assignment


The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.
Changing the interfacce of a function will likely result in a fail 
for the test of your code. This is not negotiable! 

You have to make sure that your code works with the files provided 
(search.py and sokoban.py) as your code will be tested 
with the original copies of these files. 

Last modified by 2022-03-27  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

"""

# You have to make sure that your code works with
# the files provided (search.py and sokoban.py) as your code will be tested
# with these files
import search
import sokoban

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    """
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)

    """
    return [
        (10543473, "Tarrant", "Cauchi"),
        (9734074, "Jarryd", "Stringfellow"),
        (10171517, "Chase", "Dart"),
    ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def taboo_cells(warehouse):
    """
    Identify the taboo cells of a warehouse. A "taboo cell" is by definition
    -77,14 +75,93 @@ def taboo_cells(warehouse):
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.
    """

    # some constants
    wall = '#'
    targets = ['.', '!', '*']
    unwanted = ['$', '@']
    taboo = 'X'

    def corner(wh, x, y, isWall=False):
        """
        Checks if next to a wall on left/right and up/down
        """
        # init wall count
        vertWalls = 0
        horizWalls = 0
        # check for walls above and below
        for (dx, dy) in [(0, 1), (0, -1)]:
            if wh[y + dy][x + dx] == wall:
                vertWalls += 1
        # check for walls left and right
        for (dx, dy) in [(1, 0), (-1, 0)]:
            if wh[y + dy][x + dx] == wall:
                horizWalls += 1
        if isWall:
            return (vertWalls >= 1) or (horizWalls >= 1)
        else:
            return (vertWalls >= 1) and (horizWalls >= 1)

    def Rule1(warehouse):
        """
        RULE 1: Check if a cell is a corner and not a target
        """
        wh = warehouse
        for y in range(len(wh) - 1):  # Columns
            inside = False  # Bool to check if inside or out
            for x in range(len(wh[0]) - 1):  # Rows
                if not inside:
                    if wh[y][x] == wall:  # If we have reached the wall
                        inside = True  # We are inside
                else:
                    if all([cell == ' ' for cell in wh[y][x:]]):
                        break  # We are back ouside
                    if wh[y][x] not in targets:  # Can't be taboo if it is a target
                        if wh[y][x] != wall:  # Or a wall
                            if corner(wh, x, y):
                                wh[y][x] = taboo
        return wh

    def Rule2(warehouse):
        """
        RULE 2: Check if there are any target cells between two corners
        """
        wh = warehouse
        for x in range(1, len(wh) - 1):  # Row
            for y in range(1, len(wh[0]) - 1):  # Col
                # Needs to be inline with a corner
                if wh[x][y] == taboo and corner(wh, y, x):
                    row = wh[x][y + 1:]
                    col = [row[y] for row in wh[x + 1:][:]]
                    for xin in range(len(row)):  # Inner row
                        if row[xin] in targets or row[xin] == wall:
                            break  # Can't be a target or be a wall
                        if row[xin] == taboo and corner(wh, xin + y + 1, x):
                            if all([corner(wh, xin2, x, 1)
                                    for xin2 in range(y + 1, xin + y + 1)]):
                                for xin3 in range(y + 1, xin + y + 1):
                                    wh[x][xin3] = taboo
                    for yin in range(len(col)):  # Inner col
                        if col[yin] in targets or col[yin] == wall:
                            break  # Can't be a target or be a wall
                        if col[yin] == taboo and corner(wh, y, yin + x + 1):
                            if all([corner(wh, y, yin2, 1)
                                    for yin2 in range(x + 1, yin + x + 1)]):
                                for yin3 in range(x + 1, yin + x + 1):
                                    wh[yin3][y] = taboo
        return wh

    # convert warehouse to a string
    wh_str = str(warehouse)

    # Clean the string by removing the boxes and players
    for cell in unwanted:  # If it is in list
        wh_clean = wh_str.replace(cell, ' ')  # replace with a blank

    # Rearange string to array to show full wh in 2D array
    wh_array = [list(line) for line in wh_clean.split('\n')]

    # Apply the 2 rules
    wh_array = Rule1(wh_array)
    wh_array = Rule2(wh_array)

    # Convert back into a 1D string
    wh_str = '\n'.join([''.join(line) for line in wh_array])

    # Result
    return wh_str

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class SokobanPuzzle(search.Problem):
    """
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of
    the provided module 'search.py'.

    """

    def __init__(self, warehouse):

        """
        Initialises the variables used for the Problem Solver

        @param warehouse: The chosen warehouse

        Return:
        None
        """
        # Check there are enough targets for all boxes
        assert len(warehouse.targets) >= len(warehouse.boxes)
        self.initial = tuple(warehouse.boxes), tuple(warehouse.worker)
        self.problem = warehouse
        self.taboo = taboo_calc(warehouse)

    def actions(self, state):
        """
        @param state: The current state

        Return:
         The list of actions that can be executed in the given state.

        """
        # list of actions that can be taken
        L = []  

        # Nested If statement that checks if each action
        # is possible to execute for the worker

        if legal_check(self.problem, state, 'Up') != 'Impossible':
            if taboo_check(self.taboo, state, 'Up') != 'taboo':
                L.append('Up')

        if legal_check(self.problem, state, 'Down') != 'Impossible':
            if taboo_check(self.taboo, state, 'Down') != 'taboo':
                L.append('Down')

        if legal_check(self.problem, state, 'Left') != 'Impossible':
            if taboo_check(self.taboo, state, 'Left') != 'taboo':
                L.append('Left')
                
        if legal_check(self.problem, state, 'Right') != 'Impossible':
            if taboo_check(self.taboo, state, 'Right') != 'taboo':
                L.append('Right')

        return L

    def result(self, state, action):
        """
        @param state: The current state of the warehouse
        @param action: a list of actions

        Return:
         The state that results from executing the given
         action in the given state. The action must be one of
         self.actions(state).
        """

        next_state = state
        next_state = make_move(next_state, action)
        return tuple(next_state)

    def goal_test(self, state):
        """
        Input:
         state: A state that is compared to the completed state

        Return:
         True if all boxes in warehouse are on a target.
        """
        boxes = state[0]
        if (set(boxes).issubset(set(self.problem.targets))):
            return True
        return False

    def path_cost(self, c, state1, action, state2):
        """
        Path_cost provides the path cost from one state to another based on an action list
        
        @param c: The current cost of the state
        @param state1: The curent state of the warehouse
        @param action: A list of actions
        @param state2: The target state

        Return:
          The cost of a solution path that arrives at state2 from
          state1 via action, asdist_suming cost c to get up to state1. If the problem
          is such that the path doesn't matter, this function will only look at
          state2.  If the path does matter, it will consider c and maybe state1
          and action. The default method costs 1 for every step in the path."""

        boxes_old = state1[0]
        boxes_new = state2[0]
        counter = 0

        # Added for each action
        if action:
            c = c + 1

        assert len(boxes_old) == len(boxes_new)

        #While loop counting the movement of each box from old to new
        while counter < len(boxes_old):
            diff = manhattan(boxes_old[counter], boxes_new[counter])

            # If statement to determine once a box_old has reached box_new
            if diff > 0:
                weight = self.problem.weights[counter]
                box_push = diff * weight
                c = c + box_push
            counter = counter + 1
        
        #returns path cost
        return c

    def h(self, n):
        """
        Heuristic for goal state; the estimated movement cost

        The Heuristic uses the Manhattan distance formula to
        calcuate the distance between the box and their targets,
        as well as the distance between worker and the boxes.

        @param n: n parameter

        Returns:
            Int representing the estimated remaining cost to reach goal state from current state
        """
        boxes = list(n.state[0])
        targets = list(self.problem.targets)
        worker = list(n.state[1])
        weight = zip(n.state[0], self.problem.weights)

        # Variable for the sum of the distance
        dist_sum = 0 

        # Calculating the distance between the targets and the boxes with there weights
        for box, weight in weight:
            b_t = [manhattan(box, target) for target, target in enumerate(targets)]
            dist_sum = dist_sum + min(b_t) + (min(b_t)*weight)

        # Calculates the distance from the worker and the boxes
        w_b = [manhattan(worker, box) for box, box in enumerate(boxes)]
        dist_sum = dist_sum + min(w_b) - 1

        # returns the final value from the total distances
        return dist_sum


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def manhattan(co_1, co_2):
    """
    Calcualtes manhattan distance between two coordiante tuples
   
    @param co_1: first coordinate tuple 

    @param co_2: second coordinate tuple 

    Return:
        Absolute distance between two coordinates    
    """

    manhattan = (abs(co_1[0] - co_2[0]) +
                 abs(co_1[1] - co_2[1]))
    return manhattan

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def calculate_move(state, move):
    """
    Calculates the tiles to consider in the direction of a given move ('Up', 'Down', 'Left', 'Right')

    @param State: The current state of the warehouse
    @param move: The next move of the worker

    Return:
        explore_titles provides the tile one step ahead
        explore_more provides the tile two steps ahead 
    """
    worker = state[1]
    coordinate_change = (0, 0)
    if move == 'Up':
        coordinate_change = (0, -1)
    elif move == 'Down':
        coordinate_change = (0, 1)
    elif move == 'Left':
        coordinate_change = (-1, 0)
    elif move == 'Right':
        coordinate_change = (1, 0)

    explore_tile = (worker[0] + coordinate_change[0],
                    worker[1] + coordinate_change[1])  # One tile ahead

    explore_more = (explore_tile[0] + coordinate_change[0],
                    explore_tile[1] + coordinate_change[1])  # One tile further ahead

    return explore_tile, explore_more

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def taboo_calc(warehouse):
    """
    finds coordinates of taboo cells in warehouse

    @param return: returns list of tuple coordinates of taboo cell locations in warehouse e.g. [(3,5), (7,2), (8,4)]
    """
    wh = taboo_cells(warehouse)
    lines = wh.split(sep="\n")

    return list(sokoban.find_2D_iterator(lines, "X"))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def taboo_check(taboo_locations, state, move):
    """
    checks if given move pushes box into taboo cell

    @param tabboo_locations: coordiantes of taboo cells e.g. [(3,5), (7,2), (8,4)]

    @param state: current state of problem

    @param move: move to be executed from given state

    @param return: 'tabboo' if moving box into tabboo cell
    """
    explore_tile, explore_more = calculate_move(state, move)
    boxes = state[0]
    t_l = taboo_locations
    
    # For all boxes in current state, if any (boxes) are on the first tile infront of the worker, add to list of obstrucitons
    obstruction_close = [element for element,
                         element in enumerate(boxes) if element == explore_tile]

    # If box where worker wants to go                     
    if len(obstruction_close) != 0:  
        
        # if pushing box into taboo cell
        if binary_tuple_search(explore_more, t_l) != -1:
            return 'tabboo'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def legal_check(warehouse, state, move):
    """
    Checks if given move is legal in given state

    # LEGAL CONDITIONS:
    # Cant walk through wall
    # Cant push box through wall
    # Cant push two boxes at same time

    @param warehouse: a valid Warehouse object

    @param state: a state of the warehouse object

    @param move: a move to check

    @param return: 'Impossible' if move does not satisfy all legal conditions
    """

    explore_tile, explore_more = calculate_move(state, move)
    boxes = state[0]

    # For all boxes in current state, if any (boxes) are on the first tile
    #  infront of the worker, add to list of obstrucitons
    push = [element for element, element in enumerate(
        boxes) if element == explore_tile]
    push_into = [element for element, element in enumerate(
        boxes) if element == explore_more]  # 2 tiles in front

    if binary_tuple_search(explore_tile, warehouse.walls) != -1:  # If wall
        return 'Impossible'

    if len(push) != 0:  # If box
        # If wall OR box
        if binary_tuple_search(explore_more, warehouse.walls) != -1 or len(push_into) != 0:
            return 'Impossible'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def make_move(state, move):
    """
    Makes an already checked legal move in a given state

    @param state: a state of a problem

    @param move: a valid move
    """
    explore_tile, explore_more = calculate_move(state, move)
    worker = list(state[1])
    boxes = list(state[0])

    # For all boxes in current state, if any (boxes) are on the first tile infront of
    # the worker, add to list of obstrucitons # Check if tile in front of worker has box on it

    push = [(element, i) for i, element in enumerate(boxes) if element == explore_tile]

    # If box in front of worker
    if len(push) != 0:
        boxes[push[0][1]] = explore_more # Push box
        
    worker = explore_tile  # Move worker forward
    return tuple(boxes), tuple(worker)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def binary_tuple_search(target, list):
    """
    WARNING: ONLY USE FOR STATIC SORTED LISTS (E.G. WALLS, TARGETS)

    Binary Tuple Search (More efficiently searches for a given tuple in a large, sorted list of tuples such as walls)

    @param target: a coordinate tuple E.g. (4,0)

    @param list: a sorted list of coordinate tuples E.g. [(2,0),(3,0),(4,0),(0,1),(1,1)]

    @return: index of target in list, -1 if not present
    """
    l = 0
    r = len(list) - 1
    while l <= r:
        m = (l + r) // 2
        if target == list[m]:
            return m
        elif target[::-1] > list[m][::-1]:
            l = m + 1
        else:
            r = m - 1
    return -1

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def check_elem_action_seq(warehouse, action_seq):
    """
    Determine if the sequence of actions listed in 'action_seq' is legal or not.

    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.

    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']

    @return
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    """
    state = tuple(warehouse.boxes), tuple(warehouse.worker)
    for move in action_seq:
        if legal_check(warehouse, state, move) == 'Impossible':
            return 'Impossible'
        else:
            new_state = make_move(state, move)
            warehouse.boxes = new_state[0]
            warehouse.worker = new_state[1]

    # Return string representing state of warehouse after applying sequence of actions
    return warehouse.__str__()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def trace_path(node):
    path = []
    while node.parent:
        path.insert(0, node.action)  # insert at index 0 (start)
        node = node.parent
    return path  # ['Left', 'Down', Down','Right', 'Up', 'Down']

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def solve_weighted_sokoban(warehouse):
    """
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution.
    The second item is the total cost of this action sequence.

    @param
     warehouse: a valid Warehouse object

    @return

        If puzzle cannot be solved
            return 'Impossible', None       SHOULD BE 'impossible' as its whats defined in the gui_sokoban comparison

        If a solution was found,
            return S, C
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C
    """
    sp = SokobanPuzzle(warehouse)
    sol_ts = search.astar_graph_search(sp)  # graph search version
    if sol_ts:
        S = trace_path(sol_ts)  # trace path to solution node
        C = sol_ts.path_cost

        # check_elem_action_seq(sp.problem, action_seq)
        return S, C
    return "impossible", None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":

    wh = sokoban.Warehouse()
    wh.load_warehouse("./warehouses/warehouse_155.txt")
    solve_weighted_sokoban(wh)
