import random
from node import Node

# Helper Functions

# Generates a random solvable state for the given final state in the assignment document.
# For this case a solvable state must have an odd number of inversions
def generateState():
    done = False
    while not done:
        lst = random.sample(range(0,9), 9)
        inversions = 0
        for i in range(0, len(lst)):
            for j in range(i+1, len(lst)):
                if lst[i] == 0 or lst[j] == 0:
                    continue
                inversions += 1 if (lst[j] < lst[i]) else 0
        if inversions % 2 != 0:
            done = True
            
    string = ("(" + " ".join(map(str, lst)) + ")").replace('0', 'B')
    return string

# Converts the input representation of a state in string form into a list 
def parseState(state):
    if not isinstance(state, list):
        stateToReturn = state.replace(" ", "")
        return(list(stateToReturn[1:len(stateToReturn)-1]))
    return state

# Returns a copy of any given state
def deepcopy(state):
    return([row[:] for row in state])

# Prints the state in a board like arrangement for ease of display
def printState(node, file):
    f = open(file, 'a')
    state = node.getState()
    toPrint = ""
    for idx, elem in enumerate(state):
        if (idx) % 3 == 0:
            toPrint += "\n" + str(elem)
        else:
            toPrint += " " + str(elem)
    toPrint = toPrint.replace('B', '_') + "\n"
    f.write(toPrint)
    f.close()

# Generates successor states for any given state
def successorStateGenerator(curr_node):
    states = []
    
    # Row and column containing the blank entry
    blankRow = curr_node.getState().index('B') // 3
    blankCol = curr_node.getState().index('B') % 3
    
    # Seperate into each row and create a 2D array configuration of the board
    r1, r2, r3 = curr_node.getState()[:3], curr_node.getState()[3: 6], curr_node.getState()[6:9]
    state2d = [r1, r2, r3]
    
    # For each direction below
        # Check if valid move is possible and then swap elements around
        # Create new node object to represent the new state
        # Add new node object to return list
    # return the list
    
    # LEFT
    newRow, newCol  = blankRow, blankCol - 1
    if newRow in range(0, 3) and newCol in range(0, 3):
        leftState = deepcopy(state2d)
        leftState[blankRow][blankCol], leftState[newRow][newCol] = leftState[newRow][newCol], leftState[blankRow][blankCol]
        leftState = sum(leftState, [])
        toAppend = Node(leftState, curr_node, curr_node.getDepth()+1)
        states.append(toAppend)

    # UP
    newRow, newCol  = blankRow - 1, blankCol
    if newRow in range(0, 3) and newCol in range(0, 3):
        upState = deepcopy(state2d)
        upState[blankRow][blankCol], upState[newRow][newCol] = upState[newRow][newCol], upState[blankRow][blankCol]
        upState = sum(upState, [])
        toAppend = Node(upState, curr_node, curr_node.getDepth()+1)
        states.append(toAppend)
    
    # RIGHT
    newRow, newCol  = blankRow, blankCol + 1
    if newRow in range(0, 3) and newCol in range(0, 3):
        rightState = deepcopy(state2d)
        rightState[blankRow][blankCol], rightState[newRow][newCol] = rightState[newRow][newCol], rightState[blankRow][blankCol]
        rightState = sum(rightState, [])
        toAppend = Node(rightState, curr_node, curr_node.getDepth()+1)
        states.append(toAppend)
    
    # DOWN
    newRow, newCol  = blankRow + 1, blankCol
    if newRow in range(0, 3) and newCol in range(0, 3):
        downState = deepcopy(state2d)
        downState[blankRow][blankCol], downState[newRow][newCol] = downState[newRow][newCol], downState[blankRow][blankCol]
        downState = sum(downState, [])
        toAppend = Node(downState, curr_node, curr_node.getDepth()+1)
        states.append(toAppend)
        
    return states

# Print the shortest solution path obtained from any search
def solutionPath(node, file):
    if node.getParent() == None:
        return
    else:
        solutionPath(node.getParent(), file)
        printState(node, file)

# Print the length of the shortest solution path obtained from any search
def solutionPathCost(node, ncalls=0):
    if node.getParent() == None:
        return ncalls
    else:
        return solutionPathCost(node.getParent(), ncalls+1)

# Insert node element into open list based on heuristic value
def insert(list, n, goal_node, heuristic, aStar):
    index = len(list)
    
    # If A* consider path cost too
    if aStar:
        for i in range(len(list)):
            if heuristic(list[i], goal_node) + list[i].depth > heuristic(n, goal_node) + n.depth:
                index = i
                break
    else:
        for i in range(len(list)):
            if heuristic(list[i], goal_node) > heuristic(n,goal_node):
                index = i
                break
  
    # Inserting n in the list
    if index == len(list):
      list = list[:index] + [n]
    else:
      list = list[:index] + [n] + list[index:]
    return list

# Helper function for (Inadmissible) Nilsson heuristic
# Returns elements of state in clockwise order from start state
def clockwiseStates(node):
    curr_state = node.getState()
    clockwiseIndices = [0,1,2,5,8,7,6,3]
    clockwiseState = []
    toReturn = []

    for index in clockwiseIndices:
        clockwiseState.append(curr_state[index])

    startBlank = True if clockwiseState[0] == 'B' else False

    for i in range(1, len(clockwiseState)):
        curr_pair = (clockwiseState[i-1], clockwiseState[i])
        toReturn.append(curr_pair)
    
    if startBlank:
        toReturn.append((clockwiseState[-1], 'B'))
    else:
        toReturn.append((clockwiseState[-1], clockwiseState[0]))
    
    for elem in toReturn:
        if elem[0] == 'B':
            toReturn.remove(elem)

    return toReturn

# Inadmissible Heuristic
# distance = Manhattan Distance
# center = 1 if center element is not equal to goal state center element
# successors = number of mismatch of elements in clockwise orientation
# (See last page of Analysis.pdf for clearer explanation)
def nilssonHeuristic(node, goal_node):
    score = 0
    distances = manhattanDistance(node, goal_node)
    
    curr_state = node.getState()
    goal_state = goal_node.getState()
    
    curr_state_middle = curr_state[int((len(curr_state)-1) / 2)]
    goal_state_middle = goal_state[int((len(goal_state)-1) / 2)]
    
    center = 1 if curr_state_middle != goal_state_middle else 0
    
    curr_clockwise = clockwiseStates(node)
    goal_clockwise = clockwiseStates(goal_node)
    
    successors = len(list(set(curr_clockwise) - set(goal_clockwise)))
    
    score = distances + 3*(center + 2*successors)
    
    return score

# Admissible Heuristics

# Count number of misplaced tiles
def hammingDistance(node, goal_node):
    x = 0
    node_state = node.getState()
    goal_state = goal_node.getState()
    for i in range(len(node_state)):
        if node_state[i] != goal_state[i]:
            x += 1
    return x

# Count sum of horizontal and vertical distances of misplaced tiles
def manhattanDistance(node,goal_node):
    dist = 0   
    for elem in node.getState():
        if elem != "B":
            currX = node.getState().index(elem) // 3
            currY = node.getState().index(elem) % 3
            goalX = goal_node.getState().index(elem) // 3
            goalY = goal_node.getState().index(elem) % 3
            dist += abs(currX-goalX) + abs(currY - goalY)
    return dist

# For each tile, count how many tiles on its right should be on its left in the goal state. 
def permutationInverse(node, goal_node):
    goal_state = goal_node.getState()
    initial_state = node.getState()
    x = 0
    
    for k, i in enumerate(initial_state):
        if i != 'B':
            idx = goal_state.index(i)
            nums = goal_state[:idx]
            for j in range(k+1, len(initial_state)):
                if initial_state[j] != 'B':
                    if initial_state[j] in nums:
                        x += 1
    return x

# Search Algorithms

# Depth first search (Uninformed Search)
def DFS(start_node, goal_node, file):
    
    goal_node = Node(parseState(goal_node), None, 0)
    start_node = Node(parseState(start_node), None, 0)
    
    # Initialize open as a stack
    open_lst = [start_node]
    closed = []
    nodes_explored = 0
    
    # Begin iteration
    while len(open_lst) != 0:
        
        # Pop from stack and check if it is the goal state
        x = open_lst.pop(-1)
        nodes_explored += 1
        if x.getState() == goal_node.getState():
            break
        else:
            
            # Generate list of children
            children = successorStateGenerator(x)
            closed.append(x)
            
            # Insert child into open appropriately
            for child in children:
                if child.getState() in list(map(Node.getState, open_lst)) or child.getState() in list(map(Node.getState, closed)):
                    continue
                else:
                    open_lst.append(child)
    
    # Once solution is found show stats and search path

    f = open(file, 'w')
    f.write("Nodes Explored: " + str(nodes_explored))
    f.write("\nSolution Path Length: " + str(solutionPathCost(x))+"\n")
    f.write("\nInitial State:")
    f.close()
    printState(start_node, file)
    solutionPath(x, file)


# Breadth first search (Uninformed Search)
def BFS(start_node, goal_node, file):
    
    goal_node = Node(parseState(goal_node), None, 0)
    start_node = Node(parseState(start_node), None, 0)
    
    # Initialize open as a queue
    open_lst = [start_node]
    closed = []
    nodes_explored = 0
    
    # Begin iteration
    while len(open_lst) != 0:
        
        # Pop from queue and check if it is the goal state
        x = open_lst.pop(0)
        nodes_explored += 1
        if x.getState() == goal_node.getState():
            break
        else:
            
            # Generate list of children
            children = successorStateGenerator(x)
            closed.append(x)
            
            # Insert child into open appropriately 
            for child in children:
                if child.getState() in list(map(Node.getState, open_lst)) or child.getState() in list(map(Node.getState, closed)):
                    continue
                else:
                    open_lst.append(child)
                    
    # Once solution is found show stats and search path

    f = open(file, 'w')
    f.write("Nodes Explored: " + str(nodes_explored))
    f.write("\nSolution Path Length: " + str(solutionPathCost(x))+"\n")
    f.write("\nInitial State:")
    f.close()
    printState(start_node, file)
    solutionPath(x, file)
  
  
# Best first search (Informed)
def bestFirst(start_node, goal_node, heuristic, file):
    
    goal_node = Node(parseState(goal_node), None, 0)
    start_node = Node(parseState(start_node), None, 0)
    
    # Initialize open as a priority queue
    open_lst = [start_node]
    closed = []
    nodes_explored = 0

    # Begin iteration
    while len(open_lst) != 0:
        
        # Pop from priority queue and check if it is goal state
        x = open_lst.pop(0)
        nodes_explored += 1
        if x.getState() == goal_node.getState():
            break
        else:
            
            # Generate list of children
            children = successorStateGenerator(x)
            closed.append(x)
            
            # Insert child into open appropriately 
            for child in children:
                if child.getState() in list(map(Node.getState, open_lst)) or child.getState() in list(map(Node.getState, closed)):
                    continue
                else:
                    open_lst = insert(open_lst, child, goal_node, heuristic, False)


    
    # Once solution is found show stats and search path

    f = open(file, 'w')
    f.write("Nodes Explored: " + str(nodes_explored))
    f.write("\nSolution Path Length: " + str(solutionPathCost(x))+"\n")
    f.write("\nInitial State:")
    f.close()
    printState(start_node, file)
    solutionPath(x, file)

# A* Search (Informed)
def Astar(start_node, goal_node, heuristic, file):
    
    goal_node = Node(parseState(goal_node), None, 0)
    start_node = Node(parseState(start_node), None, 0)
    
    # Initialize open as a priority queue
    open_lst = [start_node]
    closed = []
    nodes_explored = 0
    
    # Begin iteration
    while len(open_lst) != 0:
        
        # Pop from priority queue and check if it is a goal state
        x = open_lst.pop(0)
        nodes_explored += 1
        if x.getState() == goal_node.getState():
            break
        else:
            # Generate list of children
            children = successorStateGenerator(x)
            closed.append(x)
            
            # Insert child into open appropriately
            for child in children:
                
                # If child state already in closed
                if child.getState() in list(map(Node.getState, closed)):
                    
                    # Save index of child in closed
                    i = list(map(Node.getState, closed)).index(child.getState())

                    # If f score of child in closed greater than f score of new child
                    if heuristic(closed[i], goal_node) + closed[i].getDepth() > heuristic(child, goal_node) + child.getDepth():
                        
                        # Add to open list
                        open_lst = insert(open_lst, child, goal_node, heuristic, True)
                
                # Elif child state already in open list
                elif child.getState() in list(map(Node.getState, open_lst)):
                    
                    # Save index of child in open list
                    i = list(map(Node.getState, open_lst)).index(child.getState())
                    
                    # If f score of child in open list greater than f score of new child
                    if heuristic(open_lst[i], goal_node) + open_lst[i].getDepth() > heuristic(child, goal_node) + child.getDepth():
                        
                        # Add to open list
                        open_lst = insert(open_lst, child, goal_node, heuristic, True)
                        
                else:
                    
                    # Add to open list
                    open_lst = insert(open_lst, child, goal_node, heuristic, True)



    # Once solution is found show stats and search path
    f = open(file, 'w')
    f.write("Nodes Explored: " + str(nodes_explored))
    f.write("\nSolution Path Length: " + str(solutionPathCost(x))+"\n")
    f.write("\nInitial State:")
    f.close()
    printState(start_node, file)
    solutionPath(x, file)


def main():
    
    
    # Once search.py is run a random state will be generated
    
    '''
    Heuristics:
        Hamming Distance = hammingDistance
        Manhattan Distance = manhattanDistance
        Permutation Inverse = permutationInverse
        Nilsson's Heuristic (Inadmissible) = nilssonHeuristic
    '''
    
    '''
    Searches:
        Breadth First Search = BFS(start_node, goal_node, file)
        Depth First Search = DFS(start_node, goal_node, file)
        Best First = bestFirst(start_node, goal_node, heuristic, file)
        A* = Astar(start_node, goal_node, heuristic, file)        
    '''
    
    new_state = generateState()
    
    print("\nStart State: " + new_state + "\n")
    
    start_node = new_state
    goal_node = '(1 2 3 8 B 4 7 6 5)'

    Astar(start_node, goal_node, manhattanDistance, file = "Last run.txt")
        
            

if __name__ == "__main__":
    main()