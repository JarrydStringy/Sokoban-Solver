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

import time
# You have to make sure that your code works with
# the files provided (search.py and sokoban.py) as your code will be tested
# with these files
from asyncore import read
from math import floor

from matplotlib.pyplot import box

import search
import sokoban
from search import astar_graph_search
from sokoban import find_2D_iterator

#from sqlalchemy import false, true

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
        #init wall count
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

    def Rule1(wh):
        """
        RULE 1: Check if a cell is a corner and not a target
        """
        for y in range(len(wh) - 1):            #Columns
            inside = False                      #Bool to check if inside or out
            for x in range(len(wh[0]) - 1):     #Rows
                if not inside:
                    if wh[y][x] == wall:        #If we have reached the wall
                        inside = True           #We are inside
                else:
                    if all([cell == ' ' for cell in wh[y][x:]]):
                        break                   #We are back ouside
                    if wh[y][x] not in targets: #Can't be taboo if it is a target
                        if wh[y][x] != wall:    #Or a wall
                            if corner(wh, x, y):
                                wh[y][x] = taboo
        return wh
    
    def Rule2(wh):
        """
        RULE 2: Check if there are any target cells between two corners
        """
        for x in range(1, len(wh) - 1):                     #Row
            for y in range(1, len(wh[0]) - 1):              #Col
                if wh[x][y] == taboo and corner(wh, y, x):  #Needs to be inline with a corner
                    row = wh[x][y + 1:]
                    col = [row[y] for row in wh[x + 1:][:]]
                    for xin in range(len(row)):             #Inner row
                        if row[xin] in targets or row[xin] == wall:
                            break                           #Can't be a target or be a wall
                        if row[xin] == taboo and corner(wh, xin + y + 1, x):
                            if all([corner(wh, xin2, x, 1)
                                for xin2 in range(y + 1, xin + y + 1)]):
                                    for xin3 in range(y + 1, xin + y + 1):
                                        wh[x][xin3] = taboo
                    for yin in range(len(col)):             #Inner col
                        if col[yin] in targets or col[yin] == wall:
                            break                           #Can't be a target or be a wall
                        if col[yin] == taboo and corner(wh, y, yin + x + 1):
                            if all([corner(wh, y, yin2, 1)
                                for yin2 in range(x + 1, yin + x + 1)]):
                                    for yin3 in range(x + 1, yin + x + 1):
                                        wh[yin3][y] = taboo
        return wh

    #convert warehouse to a string
    wh_str = str(warehouse)
    
    #Clean the string by removing the boxes and players
    for cell in unwanted:   #If it is in list
        wh_clean = wh_str.replace(cell, ' ')    #replace with a blank
    
    #Rearange string to array to show full wh in 2D array
    wh_array = [list(line) for line in wh_clean.split('\n')]  
    
    #Apply the 2 rules
    wh_array = Rule1(wh_array)
    wh_array = Rule2(wh_array)
    
    #Convert back into a 1D string
    wh_str = '\n'.join([''.join(line) for line in wh_array])

    #Result
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
        assert len(warehouse.targets) >= len(warehouse.boxes) # Check there are enough targets for all boxes
        self.initial = tuple(warehouse.boxes), tuple(warehouse.worker)
        self.problem = warehouse
        self.taboo = taboo_calc(warehouse)
        

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.

        """
        L = []  # list of actions that can be taken

        if state == (((3, 3), (4, 2), (4, 3)),  (3,2)):  ### DELETE BEFORE SUBMISSION ###
            print("pause")

        if legal_check(self.problem, state, 'Up') != 'Impossible':
            if taboo_check(self.taboo, state, 'Up') != 'tabboo': 
                L.append('Up')
        if legal_check(self.problem, state, 'Down') != 'Impossible':
            if taboo_check(self.taboo, state, 'Down') != 'tabboo': 
                L.append('Down')
        if legal_check(self.problem, state, 'Left') != 'Impossible':
            if taboo_check(self.taboo, state, 'Left') != 'tabboo': 
                L.append('Left')
        if legal_check(self.problem, state, 'Right') != 'Impossible':
            if taboo_check(self.taboo, state, 'Right') != 'tabboo': 
                L.append('Right')

        return L

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).
        """

        next_state = state
        next_state = make_move(next_state, action)
        return tuple(next_state)

    def goal_test(self, state):
        """Return True if all boxes in warehouse are on a target.
        """
        boxes = state[0]
        if (set(boxes).issubset(set(self.problem.targets))):
            return True
        return False

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        if action:
            c = c + 1
        
        boxes_old = state1[0]
        boxes_new = state2[0]
        assert len(boxes_old) == len(boxes_new)
        counter = 0
        while counter < len(boxes_old):
            diff = dist_calc(boxes_old[counter], boxes_new[counter])
            if diff > 0:
                weight = self.problem.weights[counter]
                box_push = diff * weight
                c = c + box_push
            counter = counter + 1
        return c

    #OLD_CODE
    # def h(self, n):
    #     """
    #     Heuristic for goal state; the estimated movement cost
    #     """
    #     boxes = list(n.state[0])
    #     worker = list(n.state[1])
    #     combo = zip(boxes)

    #     misplaced = [(element, i) for i, element in enumerate(boxes) if element not in self.problem.targets] # Get weights and indicies of misplaced boxes
    #     if misplaced:
    #         worker_costs = 0
    #         for box in misplaced:
    #             b_c = boxes[box[1]] # Retrieve corresponding box coordinates
    #             distance = dist_calc(tuple(worker), b_c) - 1 # Get distance between worker and box -> distance
    #             worker_costs = worker_costs + distance
            
    #         push_costs = 0
    #         empty_targets = [(element, i) for i, element in enumerate(self.problem.targets) if element not in boxes]# Gets coordinates and index of empty targets
    #         while misplaced and empty_targets:
    #             heaviest = (max(misplaced, key = lambda t: t[0]))
    #             heaviest_index = heaviest[1] # Get index of heaviest box
    #             heaviest_box = boxes[heaviest_index] # Retrive coordinates of heaviest box
    #             distance_between = [ (dist_calc(tuple(element[0]), heaviest_box), element[1]) for element, element in enumerate(empty_targets)]  # Calculate distance heaviest box to each target.
    #             cet_info = min(distance_between, key = lambda t: t[0])
    #             cet_dist = cet_info[0] # Get distance to closest target
    #             cet_index = cet_info[1] # Get index of closest target
    #             cet = self.problem.targets[cet_index], cet_index # Retrieve coordiantes and index of closest target
    #             empty_targets.remove(cet) # Remove cet from empty_targets
    #             moving_cost = cet_dist * self.problem.weights[heaviest_index] # weight cost of moving box to target
    #             total_cost = cet_dist + moving_cost # total cost to move box to target
    #             push_costs = push_costs + total_cost
    #             misplaced.remove(heaviest) # Remove current (heaviest) box from misplaced_info
    #         return worker_costs + (push_costs // 2)
    #     else:
    #         return 0

    def h(self, n):
            """
            Heuristic for goal state; the estimated movement cost
            """
            boxes = list(n.state[0])
            targets = list(self.problem.targets)
            worker = list(n.state[1])
            weight = zip(n.state[0], self.problem.weights)
            
            sum = 0
            
            for box, weight in weight:
                b_t = [dist_calc(box, target) for target, target in enumerate(targets)]
                sum = sum + min(b_t) + (min(b_t)*weight)

            w_b = [dist_calc(worker, box) for box, box in enumerate(boxes)]
            sum = sum + min(w_b) - 1
            
            return sum
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def direction_push(something):
    return -1

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def dist_calc(co_1, co_2):
        """
        Calcualtes manhattan distance between two coordiante tuples

        @param co_1: first coordinate tuple 

        @param co_2: second coordinate tuple 
        """
        manhattan = (abs(co_1[0] - co_2[0]) +
                     abs(co_1[1] - co_2[1]))
        return manhattan

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def calculate_move(state, move):
    """
    Calculates the two tiles in the direction of a given move ('Up', 'Down', 'Left', 'Right')
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
                    explore_tile[1] + coordinate_change[1]) # One tile further ahead
    
    return explore_tile, explore_more

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def taboo_calc(warehouse):
    """
    finds coordinates of taboo cells in warehouse
    
    @param return: returns list of tuple coordinates of taboo cell locaitons in warehouse e.g. [(3,5), (7,2), (8,4)]
    """
    wh = taboo_cells(warehouse)
    lines = wh.split(sep="\n")
    
    # first_row_brick, first_column_brick = None, None
    # for row, line in enumerate(lines):
    #     brick_column = line.find("X")
    #     if brick_column >= 0:
    #         if first_row_brick is None:
    #             first_row_brick = row  # found first row with a taboo cell
    #         if first_column_brick is None:
    #             first_column_brick = brick_column
    #         else:
    #             first_column_brick = min(first_column_brick, brick_column)
                
    # lines = [
    #     line[first_column_brick:]
    #     for line in lines[first_row_brick:]
    #     if line.find("X") >= 0
    # ]
    
    return list(find_2D_iterator(lines, "X"))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def taboo_check(taboo_locations, state, move):
    """
    checks if pushing box into taboo cell
    
    @param tabboo_locations: coordiantes of taboo cells e.g. [(3,5), (7,2), (8,4)]

    @param return: 'tabboo' if moving box into tabboo cell
    """
    explore_tile, explore_more = calculate_move(state, move)
    boxes = state[0]
    t_l = taboo_locations
    obstruction_close = [element for element, element in enumerate(boxes) if element == explore_tile] # For all boxes in current state, if any (boxes) are on the first tile infront of the worker, add to list of obstrucitons
    if len(obstruction_close) != 0:  # If box where worker wants to go
        if binary_tuple_search(explore_more, t_l) != -1: # if pushing box into taboo cell
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
    """
    explore_tile, explore_more = calculate_move(state, move)
    boxes = state[0]

    push = [element for element, element in enumerate(boxes) if element == explore_tile] # For all boxes in current state, if any (boxes) are on the first tile infront of the worker, add to list of obstrucitons
    push_into = [element for element, element in enumerate(boxes) if element == explore_more] # 2 tiles in front
    
    if binary_tuple_search(explore_tile, warehouse.walls) != -1:  # If wall
        return 'Impossible'

    if len(push) != 0:  # If box
        if binary_tuple_search(explore_more, warehouse.walls) != -1 or len(push_into) != 0:  # If wall OR box
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
    push = [(element, i) for i, element in enumerate(boxes) if element == explore_tile] # For all boxes in current state, if any (boxes) are on the first tile infront of the worker, add to list of obstrucitons # Check if tile in front of worker has box on it
    if len(push) != 0: # If tile in front of worker has box
        boxes[push[0][1]] = explore_more # Push box: Replace explore_tile with explore_more
    worker = explore_tile  # move worker forward
    return tuple(boxes), tuple(worker)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def binary_tuple_search(target, list):
    """
    WARNING: ONLY USE FOR STATIC SORTED LISTS (E.G. WALLS, TARGETS)

    Binary Tuple Search (More efficiently searches for a given tuple in a LARGE, STATIC, ALWAYS SORTED list of tuples such as walls)

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
        path.insert(0, node.action) # insert at index 0 (start)
        node = node.parent
    return path # ['Left', 'Down', Down','Right', 'Up', 'Down']

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
    sol_ts = astar_graph_search(sp)  # graph search version
    if sol_ts:
        S = trace_path(sol_ts) # trace path to solution node
        C = sol_ts.path_cost
        # check_elem_action_seq(sp.problem, action_seq)
        return S, C
    return "impossible", None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":

    wh = sokoban.Warehouse()
    # wh.load_warehouse("./warehouses/warehouse_01_a.txt")
    # wh.load_warehouse("./warehouses/warehouse_09.txt")
    # wh.load_warehouse("./warehouses/warehouse_8a.txt")
    wh.load_warehouse("./warehouses/warehouse_47.txt")
    # wh.load_warehouse("./warehouses/warehouse_57.txt")


    solve_weighted_sokoban(wh)
    

    ##### check_elem_action_seq TEST #####

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Up']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Hits wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Down']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Hits wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Left']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Hits wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Right']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Hits wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Up', 'Up', 'Left', 'Left', 'Left', 'Down', 'Down', 'Left', 'Left', 'Left', 'Up', 'Up', 'Right', 'Right', 'Up', 'Right', 'Down', 'Down']
    # print(check_elem_action_seq(wh, sequence)) # Legal (Push box to target)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Up', 'Up', 'Left', 'Left', 'Left', 'Down', 'Left', 'Up']
    # print(check_elem_action_seq(wh, sequence)) # Legal (Push box up test)
    
    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Up', 'Up', 'Left', 'Left', 'Left', 'Down', 'Left', 'Up', 'Up', 'Up', 'Up']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Push box UP into wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right']
    # print(check_elem_action_seq(wh, sequence))  # Legal (Move to empty space)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Up', 'Up', 'Left', 'Left', 'Left', 'Down', 'Down', 'Left', 'Left', 'Left', 'Up', 'Up', 'Right', 'Right', 'Up', 'Right', 'Down', 'Down', 'Down']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Push box DOWN into wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Up', 'Up', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Push box LEFT into wall)

    # wh.load_warehouse("./warehouses/warehouse_03.txt")
    # sequence = ['Right', 'Up', 'Up', 'Left', 'Left', 'Left', 'Down', 'Down', 'Left', 'Left', 'Left', 'Up', 'Up', 'Right', 'Right', 'Right', 'Right', 'Right', 'Right', 'Right', 'Right']
    # print(check_elem_action_seq(wh, sequence)) # Illegal (Push box RIGHT into wall)

    ###
    # Conditions NOT tested:
    #   - Pushing two boxes in any direction
    ###

    ##### check_elem_action_seq TEST #####

    ##### Weight Box Experiment #####
    # wh.load_warehouse("./warehouses/warehouse_8a.txt")
    # sequence = ['Right']
    # print(check_elem_action_seq(wh, sequence))  # Legal (Move to empty space)
