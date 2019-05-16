import copy

class ExamplePlayer:

	# order of players
	order = ["red", "green", "blue"]
	# directions that a piece can move around
	directions = [(0,-1), (0,1), (-1,0), (1,0), (-1,1), (1,-1)]
	
	# number of players
	N = 3
	# weight list for all features selected
	# features include benefits from next step :
	# pieces will exit, average distance to destination reduction, 
	# pieces will be captured from others, pieces will get captured by others.
	weights = [4, 1, 4, -4]
	
	def __init__(self, colour):
		"""
		This method is called once at the beginning of the game to initialise
		your player. You should use this opportunity to set up your own internal
		representation of the game state, and any other information about the 
		game state you would like to maintain for the duration of the game.

		The parameter colour will be a string representing the player your 
		program will play as (Red, Green or Blue). The value will be one of the 
		strings "red", "green", or "blue" correspondingly.
		"""
		# TODO: Set up state representation.

		self.color = colour
		self.id = self.order.index(colour)
		self.state = State()
		
	def maxN(self, state, id, count):
		if(count >= self.N):
			return [state.getUtilities(), state.lastAction]
		maxUtilities = [-9999, -9999, -9999]
		bestAction = ("PASS", None)
		nextStates = state.genNextStates(id)
		for s in nextStates:
			[utilities, action] = self.maxN(s, (id + 1)%self.N, count+1)
			if utilities[id] > maxUtilities[id]:
				maxUtilities = utilities
				bestAction = s.lastAction
			# in the occasion that utilities of A player are the same,
			# we should consider the one that has largest advance than enemies
			elif utilities[id] == maxUtilities[id]:
				diffCrt = (maxUtilities[id]-maxUtilities[(id-1)%self.N]) + (maxUtilities[id]-maxUtilities[(id+1)%self.N])
				diffNext = (utilities[id]-utilities[(id-1)%self.N]) + (utilities[id]-utilities[(id+1)%self.N])
				if diffCrt < diffNext:
					maxUtilities = utilities
					bestAction = s.lastAction
		return [maxUtilities, bestAction]
		
	def action(self):
		"""
		This method is called at the beginning of each of your turns to request 
		a choice of action from your program.

		Based on the current state of the game, your player should select and 
		return an allowed action to play on this turn. If there are no allowed 
		actions, your player must return a pass instead. The action (or pass) 
		must be represented based on the above instructions for representing 
		actions.
		"""
		# TODO: Decide what action to take.
		
		[utilities, action] = self.maxN(self.state, self.id, 0)
		#print("utilities: ", utilities)
		#nextStates = self.state.genNextStates(self.id)
		#idx = int(len(nextStates)/2)
		return action


	def update(self, colour, action):
		"""
		This method is called at the end of every turn (including your player’s 
		turns) to inform your player about the most recent action. You should 
		use this opportunity to maintain your internal representation of the 
		game state and any other information about the game you are storing.

		The parameter colour will be a string representing the player whose turn
		it is (Red, Green or Blue). The value will be one of the strings "red", 
		"green", or "blue" correspondingly.

		The parameter action is a representation of the most recent action (or 
		pass) conforming to the above in- structions for representing actions.

		You may assume that action will always correspond to an allowed action 
		(or pass) for the player colour (your method does not need to validate 
		the action/pass against the game rules).
		"""
		# TODO: Update state representation in response to action.
		# get the id of the player
		id = self.order.index(colour)
		s = self.state
		ps = s.positions
		if action[0] == "PASS":
			return
		elif action[0] == "EXIT":
			ps[id].remove(action[1])
			s.exited[id] += 1
		elif action[0] == "MOVE":
			ps[id].remove(action[1][0])
			ps[id].append(action[1][1])
		# jump action, remove old position, add new one, and check mid position, 
		# capture it if possible
		else:
			ps[id].remove(action[1][0])
			ps[id].append(action[1][1])
			xMid = action[1][0][0] + int((action[1][1][0]-action[1][0][0])/2)
			yMid = action[1][0][1] + int((action[1][1][1]-action[1][0][1])/2)
			if (xMid,yMid) not in ps[id]:
				for i in range(self.N):
					if (xMid,yMid) in ps[i]:
						ps[i].remove((xMid,yMid))
						s.getCaptured[i] += 1
						break
				ps[id].append((xMid,yMid))
				s.captured[id] += 1

		# update utility vector
		#s.getUtilities()		
###################################################			
# define the class to store the state of Chexers
class State:

	# order of players
	order = ["red", "green", "blue"]
	# directions that a piece can move around
	directions = [(0,-1), (0,1), (-1,0), (1,0), (-1,1), (1,-1)]

	# number of players
	N = 3
	# weight list for all features selected
	# features include benefits from next step :
	# pieces exited, average distance to destination, 
	# pieces captured from others, pieces got captured by others.
	weights = [4, -1, 4, -4]

	# define the destination for each color piece
	destinations = [[(3,-3), (3,-2), (3,-1), (3,0)],
							[(-3,3), (-2,3), (-1,3), (0,3)],
							[(-3,0), (-2,-1), (-1,-2), (0,-3)]]

	def __init__(self):
		#initial the positions of piece in each color
		self.positions = [[(-3,0), (-3,1), (-3,2), (-3,3)],
							[(0,-3), (1,-3), (2,-3), (3,-3)],
							[(0,3), (1,2), (2,1), (3,0)]
							] 
		self.player = 0
		self.avgDistance = [999, 999, 999]
		self.exited = [0,0,0]        # to store the exited pieces for each color
		self.captured = [0,0,0]      # to store the pieces captured from other colors
		self.getCaptured = [0,0,0]   # to store the pieces get captured by others
		self.children = []
		self.lastAction = None	# record the action to generate self from parent
		self.utilityVec = [-999,-999,-999]

	# generate a copy from a state,
	# copy will inherit some necessary attributes from parent: pieces exited, 
	# pieces captured from others, pieces got captured by others
	def genCopy(self):
		cp = State()
		cp.positions = copy.deepcopy(self.positions)
		cp.exited = list(self.exited)
		cp.captured = list(self.captured)
		cp.getCaptured = list(self.getCaptured)
		return cp


	def getUtilities(self):
		self.calcAvgDis()
		for i in range(self.N):
			feature = [self.exited[i], self.avgDistance[i], self.captured[i], self.getCaptured[i]]
			self.utilityVec[i] = sum(list(map(lambda x,y:x*y, feature, self.weights)))
		return self.utilityVec
		
	# calculate the average distance to destination 
	# based on the needed closest pieces to destination
	# when the player captured many other pieces, only calculate those closest ones	
	def calcAvgDis(self):
		for i in range(self.N):
			# a list to store the shortest distance for each piece
			disList = []
			if self.exited[i] >= 4:
					self.avgDistance[i] = 0
					continue
			for (x,y) in self.positions[i]:
				temp = 99
				# find the direct distance to destination
				for (r,q) in self.destinations[i]:
					temp = min(temp, abs(x-r) + abs(y-q))
					# just make sure the estimation is smaller than the real one
				disList.append(temp)
			# when the pieces left are more than we needed, 
			# only pieces have smaller distance are counted
			# but if pieces are not enough, just cal the avg distance of all available pieces
			
			if disList != []:
				disList.sort()
				if (4-self.exited[i]) >= len(disList):
					self.avgDistance[i] = sum(disList)/len(disList)
				else:
					self.avgDistance[i] = sum(disList[0:(4-self.exited[i])])/(4-self.exited[i])
			else:
				self.avgDistance[i] = 0
		
		

	# judge whether (a,b) is inside the panel
	def isValid(self,  a,b):
		if a<-3 or a>3 or b<-3 or b>3 or (a+b)<-3 or (a+b)>3:
			return False
		return True

	# (a,b) is not occupied by some piece 
	def isVacant(self, a,b):
		for i in range(self.N):
			if (a,b) in self.positions[i]:
				return False
		return True

	#move each chexcer of current player around and return all possible states 
	def move(self):
		for (x,y) in self.positions[self.player]:
			for (r,q) in self.directions:
				if self.isValid(x+r,y+q) and self.isVacant(x+r,y+q):
					child = self.genCopy()
					pNew = child.positions
					# remove old position and add new position
					pNew[self.player].remove((x,y))
					pNew[self.player].append((x+r,y+q))
					
					child.getUtilities()
					# record the last action
					child.lastAction = ("MOVE", ((x,y), (x+r,y+q)))
					self.children.append(child)
				
		

	#jump each chexcer around and add all valid states into children
	def jump(self):
		for (x,y) in self.positions[self.player]:
			for (r,q) in self.directions:
				if not self.isVacant(x+r,y+q) and self.isValid(x+r,y+q) and self.isValid(x+2*r,y+2*q) and self.isVacant(x+2*r,y+2*q):
					child = self.genCopy()
					pNew = child.positions
					# remove old position of piece
					pNew[self.player].remove((x,y))
					# add the new position of piece
					pNew[self.player].append((x+2*r,y+2*q))
						
					# capture the intermediate piece if possible
					if (x+r, y+q) not in pNew[self.player]:
						for i in range(self.N):
							if (x+r, y+q) in pNew[i]:
								pNew[i].remove((x+r,y+q))
								# set the getCaptured features
								child.getCaptured[i] += 1
								break
						pNew[self.player].append((x+r,y+q))
						# set the capture features
						child.captured[self.player] += 1
					
					child.getUtilities()
					# record the last action
					child.lastAction = ("JUMP", ((x,y), (x+2*r,y+2*q)))
					
					self.children.append(child)

	# exit action, check any piece is on the destination coordination, if yes then exit
	def exit(self):
		for (x,y) in self.positions[self.player]:
			if (x,y) in self.destinations[self.player]:
				child = self.genCopy()
				pNew = child.positions
				# remove old position of piece
				pNew[self.player].remove((x,y))
				# record the last action
				child.lastAction = ("EXIT", ((x,y)))
				child.exited[self.player] += 1
				child.getUtilities()
				self.children.append(child)

	# pass action, just generate a copy of initial state, then copy all attributes
	def passAction(self):
		child = self.genCopy()
		child.avgDistance = list(self.avgDistance)
		child.utilityVec = list(self.utilityVec)
		child.lastAction = ("PASS", None)
		self.children.append(child)
		
		
	# generate the possible states after next step is taken
	def genNextStates(self, player):
		self.player = player
		self.children = []
		self.exit()
		self.jump()
		self.move()
		if self.children == []:
			self.passAction()
		return self.children

		
		
def main():
	pR = ExamplePlayer("red")
	pG = ExamplePlayer("green")
	pB = ExamplePlayer("blue")
	cList = ["red", "green", "blue"]
	pList = [pR, pG, pB]
	N = 3
	for i in range(10):
		print("round ", i, "----------------------")
		for j in range(N):
			actionX = pList[j].action()
			print("action of ", cList[j], "is ", actionX)
			for k in range(N):
				pList[k].update(cList[j], actionX)
				print("position of ", cList[k])
				print(pList[k].state.positions)
		print("----------------------")
			
# if __name__ == '__main__':
# 	main()
		