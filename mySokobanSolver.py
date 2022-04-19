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
from math import floor

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
        (123, "Chase", "Dart"),
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
    
    #Cells in the grid
    taboo = 'X'
    wall = '#'
    targets = ['.', '!', '*']    
    unwanted = ['$', '@']
    
    #Can use itertools.combination for finding the corners
    #Checks if next to a wall on left/right and up/down
    def Corner(warehouse, x, y, wall=False):
        vertWalls = 0
        horizWalls = 0
        wall
        #Check for walls above and below
        for (dx, dy) in [(0, 1), (0, -1)]:
            if warehouse[y + dy][x + dx] == wall:
                vertWalls += 1
        #Check for walls left and right
        for (dx, dy) in [(1, 0), (-1, 0)]:
            if warehouse[y + dy][x + dx] == wall:
                horizWalls += 1
        if wall:
            return (vertWalls >= 1) or (horizWalls >= 1)
        else:
            return (vertWalls >= 1) and (horizWalls >= 1)
    
    #RULE 1: Check if a cell is a corner and not a target
    def Rule1(warehouse):
        inside = False                                  #Bool to check if inside or out
        for y in range(len(warehouse) - 1):             #Columns
            for x in range(len(warehouse) - 1):         #Rows
                if not inside:
                    if warehouse[y][x] == wall:         #If we have reached the wall
                        inside = True                   #We are inside
                else:
                    if all([cell == ' ' for cell in warehouse[y][x:]]):
                        break                           #We are back ouside
                        
                    if warehouse[y][x] not in targets:  #Can't be taboo if it is a target
                        if warehouse[y][x] != wall:     #Or a wall
                            if Corner(warehouse, x, y):
                                warehouse[y][x] = taboo
        return warehouse
    
    #RULE 2: Check if there are any target cells between two corners
    def Rule2(warehouse):
        for y in range(1, len(warehouse) - 1):                              #Col
            for x in range(1, len(warehouse[0]) - 1):                       #Row
                if warehouse[y][x] == taboo and Corner(warehouse, x, y):    #Needs to be inline with a corner
                    row = warehouse[y][x + 1:]
                    col = [row[x] for row in warehouse[y + 1:][:]]
                    for x2 in range(len(row)):                              #Inner row
                        if row[x2] in targets or row[x2] == wall:
                            break                                           #Can't be a target or be a wall
                        if row[x2] == taboo and Corner(warehouse, x2 + x + 1, y):
                            if all([Corner(warehouse, x3, y, True) for x3 in range(x + 1, x2 + x + 1)]):
                                for x4 in range(x + 1, x2 + x + 1):
                                    warehouse[y][x4] = taboo
                    for y2 in range(len(col)):                              #Inner col
                        if col[y2] in targets or col[y2] == wall:
                            break                                           #Can't be a target or be a wall
                        if col[y2] == taboo and Corner(warehouse, x, y2 + y + 1):
                            if all([Corner(warehouse, x, y3, True) for y3 in range(y + 1, y2 + y + 1)]):
                                for y4 in range(y + 1, y2 + y + 1):
                                    warehouse[y4][x] = taboo
        return warehouse
    
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
        raise NotImplementedError()

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.

        """
        raise NotImplementedError


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

    ## LEGAL CONDITIONS:
    ##  Cant walk through wall
    ##  Cant push box through wall
    ##  Cant push two boxes at same time

    for move in action_seq:
        if move == "Up":
            coordinate_change = (0, -1)
        elif move == "Down":
            coordinate_change = (0, 1)
        elif move == "Left":
            coordinate_change = (-1, 0)
        elif move == "Right":
            coordinate_change = (1, 0)
            
        explore_tile = (warehouse.worker[0] + coordinate_change[0], warehouse.worker[1] + coordinate_change[1]) #One tile ahead
        
        if binary_tuple_search(explore_tile, warehouse.walls) != -1:   #If wall
            return 'Impossible'
        
        if binary_tuple_search(explore_tile, warehouse.boxes) != -1:   #If box
            explore_more = (explore_tile[0] + coordinate_change[0], explore_tile[1] + coordinate_change[1])  #One tile further ahead
            if binary_tuple_search(explore_more, warehouse.walls) != -1 or binary_tuple_search(explore_more, warehouse.boxes) != -1: #If wall OR box
                return 'Impossible'
            warehouse.boxes[binary_tuple_search(explore_tile, warehouse.boxes)] = explore_more #Push box: Replace explore_tile with explore_more
        
        warehouse.worker = explore_tile # move player forward
    
    print(warehouse) # Return string representing state of warehouse after applying sequence of actions


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

    raise NotImplementedError()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def binary_tuple_search(target, list):
    """
    Binary Tuple Search (More efficiently searches for a given tuple in an array of tuples)

    @param target: a coordinate tuple E.g. (4,2)

    @param list: a list of coordinate tuples E.g. [(3,6),(1,5),(4,3),(6,4),(3,5)]

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

if __name__ == "__main__":

    wh = sokoban.Warehouse()
    wh.load_warehouse("./warehouses/warehouse_03.txt")

    ### TEST binary_tuple_search
    # print(binary_tuple_search((0, 5), wh.walls))  # Present (Middle)
    # print(binary_tuple_search((6, 2), wh.walls))  # Not Present
    # print(binary_tuple_search((2, 0), wh.walls))  # Present (Start)
    # print(binary_tuple_search((8, 5), wh.walls))  # Present (End)

    ### TEST check_elem_action_seq
    # ## UP ACTION
    # ..... # Legal (Move to empty square)
    # ..... # Legal (Push box)
    # ..... # Illegal (Walk into wall)
    # ..... # Illegal (Push box into wall)
    # ..... # Illegal (Push two boxes)

    # ## DOWN ACTION
    # ..... # Legal (Move to empty square)
    # ..... # Legal (Push box)
    # ..... # Illegal (Walk into wall)
    # ..... # Illegal (Push box into wall)
    # ..... # Illegal (Push two boxes)

    # ## LEFT ACTION
    # ..... # Legal (Move to empty square)
    # ..... # Legal (Push box)
    # ..... # Illegal (Walk into wall)
    # ..... # Illegal (Push box into wall)
    # ..... # Illegal (Push two boxes)

    # ## RIGHT ACTION
    # ..... # Legal (Move to empty square)
    # ..... # Legal (Push box)
    # ..... # Illegal (Walk into wall)
    # ..... # Illegal (Push box into wall)
    # ..... # Illegal (Push two boxes)

    # ## MULTIPLE ACTIONS
    # sequence1 = ["Left", "Down", "Down", "Right", "Up", "Down"]
    # print(check_elem_action_seq(wh, sequence1)) # Legal (Push box to target)

    # sequence2 = ["Right", "Up", "Up", "Left", "Left", "Left", "Down", "Down", "Left", "Left", "Left", "Up", "Up", "Right", "Right", "Up", "Right", "Down", "Down"]
    # print(check_elem_action_seq(wh, sequence2)) # Legal (Push box to target)
    
