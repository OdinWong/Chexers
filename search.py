"""
COMP30024 Artificial Intelligence, Semester 1 2019
Solution to Project Part A: Searching

Authors: Chuan Yan
		 Odin Wong
"""

import sys
import json
from queue import PriorityQueue

nodetest = False

#global node counter
nodesgen=0

# define the class to store the state of Chexers
class State:

	#optimisation, define possible class attributes reduce memory usage
	__slots__ = ['color', 'positions', 'blocks', 'parent', 'totalCost', 'currentCost', 'estimatedCost', 'children', 'destination', 'lastAction', 'finished']

	#directions that a piece can move around
	directions = [(0,-1), (0,1), (-1,0), (1,0), (-1,1), (1,-1)]

	def __init__(self, color, positions, blocks, parent, cost):
		self.color = color	#color defines the destination
		self.positions = positions	# the positions of current pieces in 'color' color
		self.blocks = blocks	# the positions of blocks
		self.parent = parent	# record the parent for tracing back
		self.totalCost = 0		# 3 cost attribute according to f(n) = g(n) + h(n)
		self.currentCost = cost
		self.estimatedCost = 0
		self.children = []
		self.destination = []
		self.lastAction = []	# record the action to generate self from parent
		self.finished = False	# finished is true when 'positions' is empty

	# overwrite to be comparable
	def __lt__(self,other):#operator <
		return self.totalCost < other.totalCost


	# define the destination via color
	def setDestination(self):
		if self.color == "red":
			self.destination = [[3,-3], [3,-2], [3,-1], [3,0]]
		elif self.color == "green":
			self.destination = [[-3,3], [-2,3], [-1,3], [0,3]]
		else:
			self.destination = [[-3,0], [-2,-1], [-1,-2], [0,-3]]

	# define the estimated cost from current to goal
	def estimateCost(self):
		for [x,y] in self.positions:
			# just a big integer lager than all possible distance
			temp = 99
			for [r,q] in self.destination:
				temp = min(temp, abs(x-r) + abs(y-q))
			# just make sure the estimation is smaller than the real one
			if temp > 2:
				self.estimatedCost += temp - min(2, len(self.blocks))
			else:
				self.estimatedCost += temp
		self.totalCost = self.currentCost + self.estimatedCost
		return self.estimatedCost


	# [a,b] inside the panel
	def isValid(self,  a,b):
		if a<-3 or a>3 or b<-3 or b>3 or (a+b)<-3 or (a+b)>3:
			return False
		return True

	# [a,b] is not in positions and blocks
	def isVacant(self, a,b):
		if [a,b] in self.positions or [a,b] in self.blocks:
			return False
		return True

	#judge two state are the same or not by positions
	def isSame(self, state):
		if state == None:
			return False
		if len(self.positions) != len(state.positions):
			return False
		for [x,y] in self.positions:
			if [x,y] not in state.positions:
				return False
		return True

	#move each chexcer around and add all states into children
	def move(self):
		for (x,y) in self.positions:
			for (r,q) in self.directions:
				if self.isValid(x+r,y+q) and self.isVacant(x+r,y+q):
					p = list(self.positions)
					p.remove([x,y])
					# if next step is not on the destination, append to positions
					if [x+r,y+q] not in self.destination:
						p.append([x+r,y+q])

						#checking number of nodes generated
						if nodetest:
							global nodesgen
							nodesgen = nodesgen + 1

					child = State(self.color, p, self.blocks, self, self.currentCost +1)
					if not child.isSame(self.parent): #should not be the same as the grandparent
						# record the last action
						child.lastAction = [1, (x,y), (x+r,y+q)]
						if [x+r,y+q] in self.destination:
							child.lastAction.append((x+r,y+q))
						self.children.append(child)
						child.estimateCost()
						child.isCompleted()


	#jump each chexcer around and add all valid states into children
	def jump(self):
		for (x,y) in self.positions:
			for (r,q) in self.directions:
				if not self.isVacant(x+r,y+q) and self.isValid(x+r,y+q) and self.isValid(x+2*r,y+2*q) and self.isVacant(x+2*r,y+2*q):
					p = list(self.positions)
					p.remove([x,y])
					# if next step is not on the destination, append to positions
					if [x+2*r,y+2*q] not in self.destination:
						p.append([x+2*r,y+2*q])

						#checking number of nodes generated
						if nodetest:
							global nodesgen
							nodesgen = nodesgen + 1

					child = State(self.color, p, self.blocks, self, self.currentCost +1)
					if not child.isSame(self.parent): #should not be the same as the grandparent
						# record the last action
						child.lastAction = [2, (x,y), (x+2*r,y+2*q)]
						if [x+2*r,y+2*q] in self.destination:
							child.lastAction.append((x+2*r,y+2*q))
						self.children.append(child)
						child.estimateCost()
						child.isCompleted()

	def genChildren(self):
		self.setDestination()
		if self.finished:
			return
		self.move()
		self.jump()

	def getChildren(self):
		return self.children

	def	isCompleted(self):
		self.finished = len(self.positions) == 0
		return self.finished


def main():

	with open(sys.argv[1]) as file:
		data = json.load(file)
		color = data["colour"]
		pieces = data["pieces"]
		blocks = data["blocks"]

	init = State(color, pieces, blocks, None, 0)
	init.estimateCost()

	# using priorityqueue to store children nodes
	queue = PriorityQueue()

	queue.put(init)
	state = None
	isDone = False
	while not queue.empty() and not isDone:
		state = queue.get()
		if len(state.positions) == 0:
			break
		#print(queue.qsize())
		state.genChildren()
		for c in state.getChildren():
			queue.put(c)
			if c.finished:
				state = c
				isDone = True
				break


	queue = []
	# record the original steps
	stack = []
	while state.parent != None:
		stack.append(state)
		state = state.parent

	while len(stack):
		s = stack.pop()
		if s.lastAction[0] == 1:
			print("MOVE from ", s.lastAction[1], " to ", s.lastAction[2])
		else:
			print("JUMP from ", s.lastAction[1], " to ", s.lastAction[2])
		if len(s.lastAction) == 4:
			print("EXIT from ", s.lastAction[3])
	stack = []

	if nodetest:
		print(nodesgen)

# when this module is executed, run the `main` function:
if __name__ == '__main__':
	main()
