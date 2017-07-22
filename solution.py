__author__ = "Jacob Ider Chitham"
__credits__ = ["Udacity"]
__version__ = "1.0.0"
__maintainer__ = "Jacob Ider Chitham"
__email__ = "jacobic@hotmail.co.uk"
__status__ = "Submitted"

import logging

log_file = 'debug.log'
log_format = '%(asctime)s - %(levelname)s - %(message)s'
log_level = logging.DEBUG
logging.basicConfig(filename=log_file,level=log_level,format=log_format)
logging.FileHandler(filename=log_file, mode='w')

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]
                
def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dict form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. 
            If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    grid_fix = [digits if val == '.' else val for val in grid]
    return dict(zip(boxes, grid_fix))

def check_values(values):
    logging.info('Checking values for feasibility.')
    assert (len([values[box] for box in boxes if len(values[box]) != 0]))
    logging.info('Values contain no empty strings.')
    assert (len([values[box] for box in boxes if values[box] in digits]))
    logging.info('Values contain only allowed characters in order.')
    return

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The Sudoku in dict form
    """
    
    width = 1 + max(len(values[box]) for box in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in digits))
        if r in 'CF': print(line)

assignments = []

def assign_value(values, box, value):
    """
    Helper function to update values dict.
    Assigns a value to a given box. If it updates the board record it.
    
    Args:
        values(dict): a dict of the form {'box_name': '123456789', ...}
        box:
        value:

    Returns:
        The values dict after updating the box with the value.
    """

    if values[box] == value:
        return values
    logging.info('Updating box {}: {} -> {}.'.format(box, values[box], value))
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def find_twins(values):
    """Discovery component of the naked_twins function.
    
    Find all instances of naked twins.
        
    Args:
        values(dict): a dict of the form {'box_name': '123456789', ...}

    Returns:
        A dict of boxes that contain twins in the form {twin: paired_twin}. 
        Note that all twins are both a key and a value for their corresponding 
        twin.
    """
       
    logging.info('Finding naked twins in values.')
    boxes_with_twins = {}
    for box in boxes:
        for peer in peers[box]:
            if values[box] == values[peer] and len(values[box]) == 2:
                boxes_with_twins[box] = peer
    if len(boxes_with_twins) > 2:
        logging.info('Found {} pairs of naked twins.'.format(len(boxes_with_twins)))
    else: 
        logging.warn('No naked twins were found.')
    return boxes_with_twins

def eliminate_twins(values):
    """Elimination component of the naked_twins function.
    
    Eliminate all instances of naked twins from the find_twins function 
    by removing them as possibilities for their peers.
    
    Args:
        values(dict): a dict of the form {'box_name': '123456789', ...}

    Returns:
        The values dict with the naked twins eliminated from peers.
    """
     
    boxes_with_twins = find_twins(values)  
    for twin1, twin2 in boxes_with_twins.items():
        logging.info(('Eliminating twins from peers[{}], peers[{}]: ' 
                     '{}, {} -> \'\', \'\'.')
                    .format(twin1, twin2, values[twin1], values[twin2]))
        for unit in unit_list:
            if twin1 in unit and twin2 in unit:
                for box in unit:
                    if box != twin1 and box != twin2 and len(values[box]) > 1:
                        for val in values[twin1]:
                            assign_value(values, box, 
                                         values[box].replace(val, ''))
    check_values(values)
    logging.info('Current values:\n{}.'.format(values))                                     
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    
    The naked twins technique is the following. If boxes 'F3' and 'I3' both 
    permit the values of 2 and 3, both belong to the same column, but we don't 
    know which one has a 2 and which one has a 3. Despite this, the values 
    2 and 3 are locked in those two boxes, so no other box in their same unit 
    (the third column) can contain the values 2 or 3. Thus, it is possible to 
    loop over all the boxes in their (same) unit, and remove the values 2 and 
    3 from their possible values.
    
    Args:
        values(dict): a dict of the form {'box_name': '123456789', ...}

    Returns:
        The values dict with the naked twins eliminated from peers.
    """
    
    logging.info('Processing values using the naked twins technique.')
    values = eliminate_twins(values) 
    return values

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dict form.
    Returns:
        Resulting Sudoku in dict form after eliminating values.
    """
    
    logging.info('Processing values using the eliminate technique.')
    values_single = [box for box in values.keys() if len(values[box]) == 1]
    for box in values_single:
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(values[box], ''))
    check_values(values)
    logging.info('Current values:\n{}.'.format(values))     
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        values: Sudoku in dict form.
    Returns:
        Resulting Sudoku in dict form after filling in only choices.
    """
    
    logging.info('Processing values using the only choice technique.')
    for unit in unit_list:
        for dig in digits:
            boxes_with_dig = [box for box in unit if dig in values[box]] 
            if len(boxes_with_dig) == 1:
                assign_value(values, boxes_with_dig[0], dig)
    check_values(values)
    logging.info('Current values:\n{}.'.format(values))                
    return values

def reduce_puzzle(values):
    """Reduce the puzzle using a number of different techniques.

    Continually reduce the Sudoku puzzle values using the eliminate technique, 
    then the only choice technique and then the naked twins technique until the
    puzzle is 'stalled' i.e. the puzzles before and after reduction are
    identical.

    Args:
        values: Sudoku in dict form.
    Returns:
        The resulting Sudoku in dict form after reduction.
        Or False if any of the a boxes of puzzle contain no value.
    """
    
    stalled = False
    while not stalled:
        
        # Check how many boxes have a determined value.
        # Reduce Puzzle with eliminate, only choice and naked twins techniques.
        # Check how many boxes have a determined value, to compare.
        # If the puzzles before and after reduction are identical, stop loop.
        
        before_single = len([values[box] for box in boxes
                            if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values) 
        after_single = len([values[box] for box in boxes
                            if len(values[box]) == 1])
        stalled = after_single == before_single  # If no new values, stop loop. 
        if not stalled:
            logging.warn('The solution has not converged. Reprocessing again.') 
        
        # Return False if there is a box with zero available values:
        
        if (len([values[box] for box in boxes if len(values[box]) == 0])):
            logging.debug('There is an empty box. Something went wrong.')
            return False
    logging.info('The solution has converged.')      
    return(values)

def search(values):
    """Using depth-first search and propagation, create a search tree and solve.

    If a box has multiple possibilities e.g. 1, 6, 7, and 9, a search tree is
    created. Depth-first search and propagation is used to fill it in with 
    different possible values to try and solve the puzzle. For instance if the 
    function initially fills the box with 1 and it then can't be solved, it 
    tries with a 6, then with a 7, and then with a 9. If there are multiple 
    boxes each with multiple possibilities it will prioritise the boxes with 
    the fewest possible values to optimise performance.

    Args:
        values: Sudoku in dict form.
    Returns:
        Resulting Sudoku in dict form after filling in a box and attempting to
        solve.
    """
    
    # First, reduce the puzzle using the previous function
    
    values = reduce_puzzle(values)
    if values is False:
        logging.warn('Search results failed to converge to a solution.')
        return False    # Failed earlier
    if all(len(values[box]) == 1 for box in boxes): 
        return values
    
    # Choose one of the unfilled squares with the fewest possibilities
    
    lens = min([len(values[box]) for box in boxes if len(values[box]) > 1])
    option_boxes = [box for box in boxes if len(values[box]) == lens] 
    option_box = option_boxes[0]
     
    # Recursive DFS to solve each one of the resulting Sudokus, and if one 
    # returns a value (not False), this answer will be returned.
    
    for option in values[option_box]:
        logging.info('Search is being attempted to find possible solution.')
        values_search = values.copy()
        assign_value(values_search, option_box, option)
        search_results = search(values_search)
        if search_results:
            return search_results   
     
def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a Sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...
                      4....8....52.............3'
    Returns:
        The dict representation of the final Sudoku grid. 
        False if no solution exists.
    """
    
    return  search(grid_values(grid))

# Create Sudoku board including all sub-objects such as boxes, units and peers.
 
digits = '123456789'
rows = 'ABCDEFGHI'
boxes = cross(rows, digits)
row_units = [cross(r, digits) for r in rows]
col_units = [cross(rows, c) for c in digits]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') 
                for cs in ('123', '456', '789')]
diag_units = [[r + c for r,c in zip(rows,digits)],
              [r+ c for r,c in zip(rows,digits[::-1])]]
unit_list = row_units + col_units + square_units + diag_units
units = dict((box, [unit for unit in unit_list if box in unit]) 
             for box in boxes)
peers = dict((box, set(sum(units[box], [])) - set([box])) for box in boxes)

if __name__ == '__main__':    
    
    diag_sudoku_grid = ('2.............62....1....7...6..8...3...9...7...6..4'
                         '...4....8....52.............3')
    logging.info('Initial puzzle: {}'.format(grid_values(diag_sudoku_grid)))
    logging.info('Attempting to solve puzzle.')
    solved = solve(diag_sudoku_grid)
    logging.info('Final solution to puzzle:\n{}.'.format(solved))
    display(grid_values(diag_sudoku_grid))
    
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue.'
               'Not a problem! It is not a requirement.')
