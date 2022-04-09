# rushhour.py
# my own heuristic starts from line 125.
# blocking heuristic starts from line 95.

import sys

sys.setrecursionlimit(100000)  # set the recursion limit for complicated test cases


def rushhour(heuristic_option, start_node):
    """This is the interface function provided by homework prompt.

    Args:
        heuristic_option: The argument to choose which heuristics to use.
        start_node: The argument provides the initial states.

    Returns:
        None.
    """
    result_path, states_explored, total_moves = search_algorithm_a(heuristic_option, start_node)
    print_path(result_path)
    print()
    print("Total moves: " + str(total_moves))
    print("Total states explored:" + str(states_explored))


def search_algorithm_a(heuristic_option, start_node):
    """This function implements the search algorithm A*.

    Args:
        heuristic_option: The argument to choose which heuristics to use.
        start_node: The argument provides the initial states.

    Returns:
        The path, the number of stated explored, and the number of total moves.
    """
    # define three dictionaries that uses key-value pairs to record 1 : 1 heuristic value, parent relationship,
    # and individual node depth
    heuristic_dictionary = dict()
    parent_track_dictionary = dict()
    depth_dictionary = dict()

    # define and initialize necessary arguments for computing heuristics
    cur_depth = 0
    start_node_tuple = tuple(start_node)
    depth_dictionary[start_node_tuple] = 0

    # define lists as requested by the algorithm and homework
    frontier = []
    path = []
    visited_nodes = []
    generated_nodes = [start_node]
    states_explored = 0

    # compute heuristic value of the start node
    # choose which heuristics to use
    blocking_heuristic = compute_blocking_heuristics(start_node, cur_depth)
    if heuristic_option == 0:
        # associate cur_node_string and cur_block_heuristic using dictionary
        heuristic_dictionary[start_node_tuple] = blocking_heuristic
        frontier.append((start_node, heuristic_dictionary[
            start_node_tuple]))  # no need to sort here since there is only one start node

    else:  # use my own heuristics named blocking_distance_heuristics
        # blocking_distance_heuristics = blocking_heuristic + the horizontal distance between the second "X" to the exit
        blocking_distance_heuristics = compute_blocking_distance_heuristics(blocking_heuristic, start_node)
        heuristic_dictionary[start_node_tuple] = blocking_distance_heuristics
        frontier.append((start_node, heuristic_dictionary[
            start_node_tuple]))  # no need to sort here since there is only one start node

    # invoke recursion
    result_node, states_explored = state_search(frontier, states_explored, visited_nodes, parent_track_dictionary,
                                                depth_dictionary,
                                                generated_nodes, heuristic_option, heuristic_dictionary)
    # return [] if cannot find the path
    if not result_node:
        return [], states_explored, 0
    else:
        # utilize the parent_track_dictionary to make a path list one by one from result_node
        path.append(result_node)
        result_node_tuple = tuple(result_node)
        parent_node = parent_track_dictionary[result_node_tuple]  # get the parent node of the result node
        while parent_node != start_node:
            # keep getting the parent node of current node until the loop reaches the start node
            path.append(parent_node)
            cur_node = parent_node
            cur_node_tuple = tuple(cur_node)
            parent_node = parent_track_dictionary[cur_node_tuple]

        path.append(start_node)
        total_moves = len(path) - 1  # the start node is not counted as a move
        return reverse(path), states_explored, total_moves


def compute_blocking_heuristics(cur_node, cur_depth):
    """This function computes the blocking heuristics.

    Args:
        cur_node: The argument is a node.
        cur_depth: The argument is the depth of the current node.

    Returns:
        The heuristic value of current node.
    """

    # goal node
    if cur_node[2][5] == "X" and cur_node[2][4] == "X":
        return 0
    else:
        # get the position of the first letter "X"
        special_car_start_col_index = cur_node[2].index("X")
        cur_block_heuristic = 1 + cur_depth
        # iterate the third row from the right of the special car and count the number of unique letters
        blocking_vehicles = set()
        for i in range(special_car_start_col_index + 2, len(cur_node[2])):
            # check if current position equals to any letters excluding "X"
            if cur_node[2][i] != "-":
                blocking_vehicles.add(cur_node[2][i])

        # f(n) = h(n) + g(n)
        cur_block_heuristic += len(blocking_vehicles)
        return cur_block_heuristic


def compute_blocking_distance_heuristics(blocking_heuristics, cur_node):
    """This function computes my own heuristic values.

    Args:
        blocking_heuristics: The blocking heuristic value of the current node.
        cur_node: The current node.

    Returns:
        The heuristic value of current node.
    """

    # Formula: blocking_distance_heuristics = blocking_heuristic + the horizontal distance between the second "X"
    # to the exit.

    # Explanation:  If there are two cases that has the same heuristic value, I will pick the one whose special car is
    # close to the exit. For example, here are the third row of the two cases. "AAXXB-" and "AA-XXB". Both of them
    # have heuristic value 2. The horizontal distance between the second "X" to the exit(index is [2][5]) is 2 and 1
    # respectively. Therefore, I pick the latter one "AA-XXB".

    # Test result:
    # use beginner test provided in the rubric file
    # blocking heuristics VS blocking_distance heuristics
    # around 2460 - 2480  VS 1270 - 1298
    # From the result, I find blocking_distance heuristics reduces the number of explored states by half.

    # goal node
    if cur_node[2][5] == "X" and cur_node[2][4] == "X":
        return 0
    else:
        special_car_start_col_index = cur_node[2].index("X")
        distance_from_exit = 5 - (special_car_start_col_index + 1) # + 1 because the index is from the first letter "X"
        blocking_distance_heuristics = distance_from_exit + blocking_heuristics
        return blocking_distance_heuristics


def locate_vehicles(cur_node):
    """This function computes the position of the first letter of each vehicle.

    Args:
        cur_node: The current node.

    Returns:
        A list of all vehicles' code whose format is (row_index + col_index + truck or car + horizontal or vertical)
    """
    # define a list to store vehicle information
    vehicles = []

    # concatenate each row to be a string
    cur_node_string = "".join(cur_node)
    # delete the duplicate letter and empty symbol
    vehicles_categories = set(cur_node_string)
    vehicles_categories.remove("-")

    for letter in vehicles_categories:
        letter_pos = cur_node_string.index(letter)
        row_index = letter_pos // 6
        col_index = letter_pos % 6
        # define a vehicle code
        vehicle_code = str(row_index) + str(col_index)

        # check if it is a car or truck
        letter_count = cur_node_string.count(letter)
        if letter_count == 3:
            vehicle_code += "t"  # t for truck
        else:
            vehicle_code += "c"  # c for car

        # check if the vehicle is horizontal or vertical
        if cur_node_string[letter_pos + 1] == letter:
            vehicle_code += "h"  # h for horizontal
        else:
            vehicle_code += "v"  # v for vertical

        # the code format is row_index + col_index + truck or car + horizontal or vertical
        vehicles.append(vehicle_code)

    return vehicles


def state_search(frontier, states_explored, visited_nodes, parent_track_dictionary, depth_dictionary,
                 generated_nodes, heuristic_option, heuristic_dictionary):

    """This function implements repeat part of the pseudocode.

    Args:
        frontier: A list contains tuples which are the unexplored nodes and their heuristic values.
        states_explored: The number of explored nodes.
        visited_nodes: A list contains all explored nodes.
        parent_track_dictionary: A dictionary tracks each node's parent node.
        depth_dictionary: A dictionary tracks each node's depth.
        generated_nodes: A list contains all nodes that have been generated by other nodes.
        heuristic_option: The argument to control which heuristics to user.
        heuristic_dictionary: A dictionary tracks each node's heuristic value.

    Returns:
        A result node and states_explored(the number of explored nodes).
    """

    if not frontier:
        return [], states_explored

    # pop the node with least f(n)
    cur_node = frontier.pop(0)[0]
    states_explored += 1
    visited_nodes.append(cur_node)

    # check if the special car reaches the exit
    if cur_node[2][5] == "X" and cur_node[2][4] == "X":
        return cur_node, states_explored

    else:  # expand current node to get new nodes
        new_nodes = expand_chosen_node(cur_node, parent_track_dictionary, depth_dictionary, generated_nodes)
        # compute the heuristic value of each new node
        for new_node in new_nodes:
            new_node_tuple = tuple(new_node)
            new_node_depth = depth_dictionary[new_node_tuple]
            if heuristic_option == 0:
                heuristic_dictionary[new_node_tuple] = compute_blocking_heuristics(new_node, new_node_depth)
                frontier.append((new_node, heuristic_dictionary[new_node_tuple]))
            else:
                blocking_heuristic = compute_blocking_heuristics(new_node, new_node_depth)
                blocking_distance_heuristics = compute_blocking_distance_heuristics(blocking_heuristic, new_node)
                heuristic_dictionary[new_node_tuple] = blocking_distance_heuristics
                frontier.append((new_node, heuristic_dictionary[new_node_tuple]))

        # sort frontier by f(n) values
        frontier.sort(key=get_heuristic_value_from_tuple)

        # start recursion
        return state_search(frontier, states_explored, visited_nodes, parent_track_dictionary,
                            depth_dictionary,
                            generated_nodes, heuristic_option, heuristic_dictionary)


def get_heuristic_value_from_tuple(tup):
    """This function is used as a key to sort frontier.

    Args:
        tup: A tuple.

    Returns:
        The second element in the tuple.
    """
    return tup[1]


def expand_chosen_node(cur_node, parent_track_dictionary, depth_dictionary, generated_nodes):
    """This function generated new nodes for the current node..

    Args:
        cur_node: The current node.
        parent_track_dictionary: A dictionary tracks each node's parent node.
        depth_dictionary: A dictionary tracks each node's depth.
        generated_nodes: A list contains all nodes that have been generated by other nodes.

    Returns:
        A list contains all valid new nodes generated from the current node.
    """
    new_nodes = []
    # generate the list of vehicle codes
    vehicles = locate_vehicles(cur_node)

    # iterate over each vehicle and move them
    for vehicle_code in vehicles:  # row_index + col_index + category + orientation
        cur_node_depth = depth_dictionary[tuple(cur_node)]
        row_index = int(vehicle_code[0])
        col_index = int(vehicle_code[1])
        if vehicle_code[3] == "h":  # horizontal
            cur_row_string = cur_node[row_index]
            if vehicle_code[2] == "c":  # car
                # move car to left by 1
                if col_index - 1 >= 0 and cur_node[row_index][col_index - 1] == "-":
                    # replace the original strings with the new strings using slicing
                    new_row_string = cur_row_string[:col_index - 1] + cur_row_string[
                        col_index] * 2 + "-" + cur_row_string[col_index + 2:]
                    new_node = cur_node.copy()
                    new_node[row_index] = new_row_string
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)

                # move car to right by 1
                if col_index + 2 <= 5 and cur_node[row_index][col_index + 2] == "-":
                    # replace the original strings with the new strings using slicing
                    new_row_string = cur_row_string[:col_index] + "-" + cur_row_string[col_index] * 2 + cur_row_string[
                                                                                                        col_index + 3:]
                    new_node = cur_node.copy()
                    new_node[row_index] = new_row_string
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)
            else:  # truck
                # move truck to left by 1
                if col_index - 1 >= 0 and cur_node[row_index][col_index - 1] == "-":
                    # replace the original strings with the new strings using slicing
                    new_row_string = cur_row_string[:col_index - 1] + cur_row_string[
                        col_index] * 3 + "-" + cur_row_string[col_index + 3:]
                    new_node = cur_node.copy()
                    new_node[row_index] = new_row_string
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)

                # move truck to right by 1
                if col_index + 3 <= 5 and cur_node[row_index][col_index + 3] == "-":
                    # replace the original strings with the new strings using slicing
                    new_row_string = cur_row_string[:col_index] + "-" + cur_row_string[col_index] * 3 + cur_row_string[
                                                                                                        col_index + 4:]
                    new_node = cur_node.copy()
                    new_node[row_index] = new_row_string
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)

        else:  # vertical
            if vehicle_code[2] == "c":  # car
                # move car top by 1
                if row_index - 1 >= 0 and cur_node[row_index - 1][col_index] == "-":
                    # replace the original strings with the new strings using slicing
                    cur_row_string_one = cur_node[row_index - 1]
                    new_row_string_one = cur_row_string_one[:col_index] + cur_node[row_index][
                        col_index] + cur_row_string_one[col_index + 1:]
                    cur_row_string_two = cur_node[row_index + 1]
                    new_row_string_two = cur_row_string_two[:col_index] + "-" + cur_row_string_two[col_index + 1:]
                    new_node = cur_node.copy()
                    new_node[row_index - 1] = new_row_string_one
                    new_node[row_index + 1] = new_row_string_two
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)

                # move car down by 1
                if row_index + 2 <= 5 and cur_node[row_index + 2][col_index] == "-":
                    # replace the original strings with the new strings using slicing
                    cur_row_string_one = cur_node[row_index]
                    new_row_string_one = cur_row_string_one[:col_index] + "-" + cur_row_string_one[col_index + 1:]
                    cur_row_string_two = cur_node[row_index + 2]
                    new_row_string_two = cur_row_string_two[:col_index] + cur_node[row_index][
                        col_index] + cur_row_string_two[col_index + 1:]
                    new_node = cur_node.copy()
                    new_node[row_index] = new_row_string_one
                    new_node[row_index + 2] = new_row_string_two
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)
            else:  # truck
                # move truck top by 1
                if row_index - 1 >= 0 and cur_node[row_index - 1][col_index] == "-":
                    # replace the original strings with the new strings using slicing
                    cur_row_string_one = cur_node[row_index - 1]
                    new_row_string_one = cur_row_string_one[:col_index] + cur_node[row_index][
                        col_index] + cur_row_string_one[col_index + 1:]
                    cur_row_string_two = cur_node[row_index + 2]
                    new_row_string_two = cur_row_string_two[:col_index] + "-" + cur_row_string_two[col_index + 1:]
                    new_node = cur_node.copy()
                    new_node[row_index - 1] = new_row_string_one
                    new_node[row_index + 2] = new_row_string_two
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)

                # move truck down by 1
                if row_index + 3 <= 5 and cur_node[row_index + 3][col_index] == "-":
                    # replace the original strings with the new strings using slicing
                    cur_row_string_one = cur_node[row_index]
                    new_row_string_one = cur_row_string_one[:col_index] + "-" + cur_row_string_one[col_index + 1:]
                    cur_row_string_two = cur_node[row_index + 3]
                    new_row_string_two = cur_row_string_two[:col_index] + cur_node[row_index][
                        col_index] + cur_row_string_two[col_index + 1:]
                    new_node = cur_node.copy()
                    new_node[row_index] = new_row_string_one
                    new_node[row_index + 3] = new_row_string_two
                    # check if visited
                    if new_node not in generated_nodes:
                        new_nodes.append(new_node)
                        new_node_tuple = tuple(new_node)
                        # update dictionaries
                        parent_track_dictionary[new_node_tuple] = cur_node
                        depth_dictionary[new_node_tuple] = cur_node_depth + 1
                        generated_nodes.append(new_node)

    return new_nodes


def print_path(path):
    """This function is used to print the path.

    Args:
        path: The final path contains all moves.

    Returns:
        None.
    """
    for i in range(len(path)):
        node = path[i]
        for j in range(len(node)):
            print(node[j])
        print()


# some utility functions from peg_puzzle.py
def reverse(st):
    """This function is used to reverse a list.

    Args:
        st: A list.

    Returns:
        A list. (I used it to reverse the final path)
    """
    return st[::-1]
