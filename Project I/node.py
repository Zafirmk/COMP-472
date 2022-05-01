class Node:
    
    state = ""
    parent = None
    depth = -1
        
    def __init__(self, state, parent, depth) -> None:
        self.state = state
        self.parent = parent
        self.depth = depth
    
    def getState(self):
        return self.state
    
    def getDepth(self):
        return self.depth
    
    def getParent(self):
        return self.parent
    
    def __lt__(self, otherNode):
        return False