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
from sqlalchemy import false, true

import search
import sokoban
from search import astar_graph_search

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
    a cell inside a warehouse such that whenever a box get pushed on such
    a cell then the puzzle becomes unsolvable.

    Cells outside the warehouse are not taboo. It is a fail to tag an
    outside cell as taboo.

    When determining the taboo cells, you must ignore all the existing boxes,
    only consider the walls and the target  cells.
    Use only the following rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of
             these cells is a target.

    @param warehouse:
        a Warehouse object with the worker inside the warehouse

    @return
       A string representing the warehouse with only the wall cells marked with
       a '#' and the taboo cells marked with a 'X'.
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.
    """

    # Cells in the grid
    taboo = 'X'
    wall = '#'
    targets = ['.', '!', '*']
    unwanted = ['$', '@']

    # Can use itertools.combination for finding the corners
    # Checks if next to a wall on left/right and up/down
    def Corner(warehouse, x, y, wall=False):
        vertWalls = 0
        horizWalls = 0
        wall
        # Check for walls above and below
        for (dx, dy) in [(0, 1), (0, -1)]:
            if warehouse[y + dy][x + dx] == wall:
                vertWalls += 1
        # Check for walls left and right
        for (dx, dy) in [(1, 0), (-1, 0)]:
            if warehouse[y + dy][x + dx] == wall:
                horizWalls += 1
        if wall:
            return (vertWalls >= 1) or (horizWalls >= 1)
        else:
            return (vertWalls >= 1) and (horizWalls >= 1)

    # RULE 1: Check if a cell is a corner and not a target
    def Rule1(warehouse):
        inside = False  # Bool to check if inside or out
        for y in range(len(warehouse) - 1):  # Columns
            for x in range(len(warehouse) - 1):  # Rows
                if not inside:
                    if warehouse[y][x] == wall:  # If we have reached the wall
                        inside = True  # We are inside
                else:
                    if all([cell == ' ' for cell in warehouse[y][x:]]):
                        break  # We are back ouside

                    if warehouse[y][x] not in targets:  # Can't be taboo if it is a target
                        if warehouse[y][x] != wall:  # Or a wall
                            if Corner(warehouse, x, y):
                                warehouse[y][x] = taboo
        return warehouse

    # RULE 2: Check if there are any target cells between two corners
    def Rule2(warehouse):
        for y in range(1, len(warehouse) - 1):  # Col
            for x in range(1, len(warehouse[0]) - 1):  # Row
                # Needs to be inline with a corner
                if warehouse[y][x] == taboo and Corner(warehouse, x, y):
                    row = warehouse[y][x + 1:]
                    col = [row[x] for row in warehouse[y + 1:][:]]
                    for x2 in range(len(row)):  # Inner row
                        if row[x2] in targets or row[x2] == wall:
                            break  # Can't be a target or be a wall
                        if row[x2] == taboo and Corner(warehouse, x2 + x + 1, y):
                            if all([Corner(warehouse, x3, y, True) for x3 in range(x + 1, x2 + x + 1)]):
                                for x4 in range(x + 1, x2 + x + 1):
                                    warehouse[y][x4] = taboo
                    for y2 in range(len(col)):  # Inner col
                        if col[y2] in targets or col[y2] == wall:
                            break  # Can't be a target or be a wall
                        if col[y2] == taboo and Corner(warehouse, x, y2 + y + 1):
                            if all([Corner(warehouse, x, y3, True) for y3 in range(y + 1, y2 + y + 1)]):
                                for y4 in range(y + 1, y2 + y + 1):
                                    warehouse[y4][x] = taboo
        return warehouse

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

    #
    #         "INSERT YOUR CODE HERE"
    #
    #     Revisit the sliding puzzle and the pancake puzzle for inspiration!
    #
    #     Note that you will need to add several functions to
    #     complete this class. For example, a 'result' method is needed
    #     to satisfy the interface of 'search.Problem'.
    #
    #     You are allowed (and encouraged) to use auxiliary functions and classes

    def __init__(self, warehouse):
        assert len(warehouse.targets) >= len(warehouse.boxes) # Check there are enough targets for all boxes
        self.initial = tuple(warehouse.boxes), tuple(warehouse.worker)
        self.problem = warehouse
        

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.

        """
        L = []  # list of legal actions
        if legal_check(self.problem, state, 'Up') != 'Impossible':
            L.append('Up')
        if legal_check(self.problem, state, 'Down') != 'Impossible':
            L.append('Down')
        if legal_check(self.problem, state, 'Left') != 'Impossible':
            L.append('Left')
        if legal_check(self.problem, state, 'Right') != 'Impossible':
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
        if (set(state).issubset(set(self.problem.targets))):
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


    def h(self, n):
        """
        Heuristic for goal state; the estimated movement cost
        """
        boxes = list(n.state[0])
        worker = list(n.state[1])
        ### misplaced = [i for i, element in enumerate(boxes) if element not in self.problem.targets] # Find indicies of misplaced boxes
        misplaced = [(element, i) for i, element in enumerate(boxes) if element not in self.problem.targets] # Get weights and indicies of misplaced boxes
        if misplaced:
            ### misplaced_info = [(element, i) for i, element in enumerate(self.problem.weights) if i in misplaced] # Get weights and indicies of misplaced boxes

            worker_costs = 0
            for box in misplaced:
                b_c = boxes[box[1]] # Retrieve corresponding box coordinates
                distance = dist_calc(tuple(worker), b_c) - 1 # Get distance between worker and box -> distance
                worker_costs = worker_costs + distance
            
            push_costs = 0
            empty_targets = [(element, i) for i, element in enumerate(self.problem.targets) if element not in boxes]# Gets coordinates and index of empty targets
            while misplaced and empty_targets:
                heaviest = (max(misplaced, key = lambda t: t[0]))
                heaviest_index = heaviest[1] # Get index of heaviest box
                heaviest_box = boxes[heaviest_index] # Retrive coordinates of heaviest box
                distance_between = [ (dist_calc(tuple(element[0]), heaviest_box), element[1]) for element, element in enumerate(empty_targets)]  # Calculate distance heaviest box to each target.
                cet_info = min(distance_between, key = lambda t: t[0])
                cet_dist = cet_info[0] # Get distance to closest target
                cet_index = cet_info[1] # Get index of closest target
                cet = self.problem.targets[cet_index], cet_index # Retrieve coordiantes and idnex of closest target
                empty_targets.remove(cet) # Remove cet from empty_targets
                moving_cost = cet_dist * self.problem.weights[heaviest_index] # weight cost of moving box to target
                total_cost = cet_dist + moving_cost # total cost to move box to target
                push_costs = push_costs + total_cost
                misplaced.remove(heaviest) # Remove current (heaviest) box from misplaced_info
            
            return worker_costs + push_costs
        else:
            return 0

            

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
    Translates a given move ('Up', 'Down', 'Left', 'Right') into respective change in coordinates
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

    if binary_tuple_search(explore_tile, warehouse.walls) != -1:  # If wall
        return 'Impossible'

    if binary_tuple_search(explore_tile, list(boxes)) != -1:  # If box
        if binary_tuple_search(explore_more, warehouse.walls) != -1 or binary_tuple_search(explore_more, list(state[0])) != -1:  # If wall OR box
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
    push = binary_tuple_search(explore_tile, list(state[0])) # Check if tile in front of worker has box on it
    if push != -1: # If tile in front of worker has box
        boxes[push] = explore_more ###CAUSING ERROR - NOT CORRECTLY ASSIGNING NEW BOX STATE AFTER PUSH### # Push box: Replace explore_tile with explore_more
    worker = explore_tile  # move worker forward
    return tuple(boxes), tuple(worker)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def binary_tuple_search(target, list):
    """
    Binary Tuple Search (More efficiently searches for a given tuple in a sorted list of tuples)

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

def tabboo_check(warehouseString):
    return [(3, 4), (2, 8)]

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


def solve_weighted_sokoban(warehouse):
    """
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution.
    The second item is the total cost of this action sequence.

    @param
     warehouse: a valid Warehouse object

    @return

        If puzzle cannot be solved
            return 'Impossible', None

        If a solution was found,
            return S, C
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C
    """
    sp = SokobanPuzzle(warehouse)
    # t0 = time.time()
    sol_ts = astar_graph_search(sp)  # graph search version
    # t1 = time.time()
    # check_elem_action_seq(sol_ts)
    # print("A* Solver took {:.6f} seconds".format(t1 - t0))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":

    wh = sokoban.Warehouse()
    # wh.load_warehouse("./warehouses/warehouse_01_a.txt")
    wh.load_warehouse("./warehouses/warehouse_09.txt")
    # wh.load_warehouse("./warehouses/warehouse_8a.txt")
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
