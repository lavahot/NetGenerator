import random
from pynput import keyboard

INTERIOR_LOBBY = [
	("File DV6", "📂6"),
	("Password DV6", "🔑6"),
	("Password DV8", "🔑8"),
	("Skunk", "🦨"),
	("Wisp", "👻"),
	("Killer", "🔪"),
]
INTERIOR_BASIC = [
	("Hellhound", "🐺"),
	("Sabertooth", "😾"),
	("Raven x2", "🐧🐧"),
	("Hellhound", "🐺"),
	("Wisp", "👻"),
	("Raven", "🐧"),
	("Password DV6", "🔑6"),
	("File DV6", "📂6"),
	("Control Node DV6", "🎛6"),
	("Password DV6", "🔑6"),
	("Skunk", "🦨"),
	("Asp", "🐍"),
	("Scorpion", "🦂"),
	("Killer, Skunk", "🔪🦨"),
	("Wisp x3", "👻👻👻"),
	("Liche", "💀"),
]
INTERIOR_STANDARD = [
	("Hellhound x2", "🐺🐺"),
	("Hellhound, Killer", "🐺🔪"),
	("Skunk x2", "🦨🦨"),
	("Sabertooth", "😾"),
	("Scorpion", "🦂"),
	("Hellhound", "🐺"),
	("Password DV8", "🔑8"),
	("File DV8", "📂8"),
	("Control Node DV8", "🎛8"),
	("Password DV8", "🔑8"),
	("Asp", "🐍"),
	("Killer", "🔪"),
	("Liche", "💀"),
	("Asp", "🐍"),
	("Raven x3", "🐧🐧🐧"),
	("Liche, Raven", "💀🐧"),
]
INTERIOR_UNCOMMON = [
	("Kraken", "🐙"),
	("Hellhound, Scorpion", "🐺🦂"),
	("Hellhound, Killer", "🐺🔪"),
	("Raven x2", "🐧🐧"),
	("Sabertooth", "😾"),
	("Hellhound", "🐺"),
	("Password DV10", "🔑10"),
	("File DV10", "📂10"),
	("Control Node DV10", "🎛10"),
	("Password DV10", "🔑10"),
	("Killer", "🔪"),
	("Liche", "💀"),
	("Dragon", "🐲"),
	("Asp, Raven", "🐍🐧"),
	("Dragon, Wisp", "🐲👻"),
	("Giant", "👹"),
]
INTERIOR_ADVANCED = [
	("Hellhound x3", "🐺🐺🐺"),
	("Asp x2", "🐍🐍"),
	("Hellhound, Liche", "🐺💀"),
	("Wisp x3", "👻👻👻"),
	("Hellhound, Sabertooth", "🐺😾"),
	("Kraken", "🐙"),
	("Password DV12", "🔑12"),
	("File DV12", "📂12"),
	("Control Node DV12", "🎛12"),
	("Password DV12", "🔑12"),
	("Giant", "👹"),
	("Dragon", "🐲"),
	("Killer, Scorpion", "🔪🦂"),
	("Kraken", "🐙"),
	("Raven, Wisp, Hellhound", "🐧👻🐺"),
	("Dragon x2", "🐲🐲"),
]

class Floor:
	def __init__(self,level):
		self.level = level
		self.is_edge = True
		self.childs = []
		self.id = 0
		self.occupancy = -1
	def addChild(self,floor):
		self.is_edge = False
		self.childs.append(floor)
class FloorSelector:
	def __init__(self):
		self.selected = set()

	def getRandom(self):
		rolled = roll3D6()
		while rolled in self.selected:
			rolled = roll3D6()
		self.selected.add(rolled)
		return rolled 

def rollD6():
	return random.randint(1,6)
def rollD10():
	return random.randint(1,10)
def roll3D6():
	return rollD6() + rollD6() + rollD6()


def writePrintOffset(floor,currOffset):
	floor.offset = currOffset
	if floor.is_edge:
		return currOffset
	if len(floor.childs) > 0:
		currOffset = writePrintOffset(floor.childs[0],currOffset)
	for i in range(1,len(floor.childs)):
		currOffset = writePrintOffset(floor.childs[i],currOffset+1)
	return currOffset

# -1 right, -2 down
def printArchitectureMakeConnection(floor, netmap):
	netmap[(floor.level-1)*2][floor.offset*2] = floor.id
	for child in floor.childs:
		for i in range(floor.offset*2+1,child.offset*2):
			netmap[(floor.level-1)*2][i] = -1
		for j in range((floor.level-1)*2+1,(child.level-1)*2):
			netmap[j][child.offset*2] = -2
		printArchitectureMakeConnection(child,netmap)


def printArchitecture(floors):
	depth = max(floor.level for floor in floors)

	print("\nMap:")
	# findOffsets
	writePrintOffset(floors[0], 0)

	# fill grid
	width = max(floor.offset for floor in floors) + 1
	netmap = [[0] * width * 2 for row in range(depth * 2)]

	# -1 right, -2 down
	printArchitectureMakeConnection(floors[0],netmap)

	for row in netmap:
		strRow = ""
		for hit in row:
			if hit > 0:
				strRow += str(getOccupant(floors[hit-1], difficulty if hit > 2 else 0)[1])
			if hit == 0:
				strRow += "  "
			if hit == -1:
				strRow += "--"
			if hit == -2:
				strRow += "| " 
		print (strRow)

'''
# minimal size is 5 for 1 Branche, 
1 entry, 2 second floor, 3 last floor, 4 - nonBranched floor, 5 - 1st possible branch
So maximal branches is: size - 4  
'''
def getNumberOfBraches(size):
	maxBranches = size - 4
	n_branches = 0
	while (n_branches < maxBranches):
		if (rollD10() >= 7):
			n_branches +=1
		else:
			break
	return n_branches

def findNodeCandidate(all_floors, depth,can_be_edge,can_be_node):
	candidates = []
	for floor in all_floors:
		if (floor.level == 1) or (floor.level >= depth-1):
			continue
		if ((floor.is_edge) and (can_be_edge)) or ((not floor.is_edge) and (can_be_node)):
			candidates.append(floor)
	#it is not perfect If no candidate is found, just deepen it and be done with it
	if len(candidates) == 0:
		for floor in all_floors:
			if floor.level == depth:
				return floor

	selected_id = random.randint(0,len(candidates)-1)
	return candidates[selected_id]

def getArchitecture():
	n_floors = roll3D6()
	n_branches = getNumberOfBraches(n_floors)
	print ("floors:" + str(n_floors) + " branches:" + str(n_branches))
	if n_branches > 0:
		min_size_of_logest_branch = 4
		max_size_of_longest_branch = n_floors - n_branches
		#use normal distribution for depth instead linear. lets make edge cases less happening
		#Also for dice game lets use dice-like method instead Gauss random
		depth = round((random.randint(min_size_of_logest_branch,max_size_of_longest_branch) + random.randint(min_size_of_logest_branch,max_size_of_longest_branch))/2)
	else:
		depth = n_floors
	#construct main brainch
	all_floors = []
	#entrance
	floor = Floor(1)
	all_floors.append(floor)
	#other levels
	level = 1
	lastfloor = floor
	for i in range(2, depth + 1):
		floor = Floor(i)
		lastfloor.addChild(floor)
		all_floors.append(floor)
		lastfloor = floor
	# add rest of floors and create branches
	if n_branches > 0:
		remaining_nodes = n_floors - depth
		remaining_branches = n_branches
		can_be_node = True
		can_be_edge = True
		while (remaining_nodes >0):
			if remaining_nodes == remaining_branches:
				can_be_edge = False
			if remaining_branches == 0:
				can_be_node = False 
			lastfloor = findNodeCandidate(all_floors,depth,can_be_edge,can_be_node)
			# if no candidate was found the NET got deeper
			if lastfloor.level == depth:
				depth +=1
			if not lastfloor.is_edge:
				remaining_branches -=1
			floor = Floor(lastfloor.level + 1)
			lastfloor.addChild(floor)
			all_floors.append(floor)
			remaining_nodes -=1

	return all_floors
	
	#for floor in all_floors:
	#	print (f"level:{floor.level},edge:{floor.is_edge},childs:{len(floor.childs)}")
	
def setID(floor,cnt):
	cnt+=1
	floor.id = cnt
	for child in floor.childs:
		cnt = setID(child,cnt)
	return cnt

def setIDs(floors):
	setID(floors[0],0)
	
def populateLevel(floorRandom,floors):
	nextLevel = []
	for floor in floors:
		floor.occupancy = floorRandom.getRandom()
		nextLevel += floor.childs
	if len(nextLevel)>0:
		populateLevel(floorRandom,nextLevel)

def populateFloors(floors):
	first = rollD6()
	second = rollD6()
	while (first==second):
		second = rollD6()
	floor = floors[0]
	floor.occupancy = first
	floor=floor.childs[0]
	floor.occupancy = second

	floorRandom = FloorSelector()
	populateLevel(floorRandom,floor.childs)


def getDifficulty():
	print("Please select difficulty")
	print(
		"1-Basic Difficulty    | DV6  | Normal interface level 2 | Deadly bottom interface level: N/A"
	)
	print(
		"2-Standard Difficulty | DV8  | Normal interface level 4 | Deadly bottom interface level: 2"
	)
	print(
		"3-Uncommon Difficulty | DV10 | Normal interface level 6 | Deadly bottom interface level: 4"
	)
	print(
		"4-Advanced Difficulty | DV12 | Normal interface level 8 | Deadly bottom interface level: 6"
	)
	try:
		difficulty = int(input("Difficulty:"))
		if not (difficulty >= 1 and difficulty <= 4):
			raise ValueError
	except ValueError:
		print("\n!!ERROR!!")
		print("Provide a number between 1 and 4")
		print("!!ERROR!!\n")
		return getDifficulty()
	return difficulty

def getOccupantsFromDifficulty(difficulty):
	difficultyMap = {
		0: INTERIOR_LOBBY,
		1: INTERIOR_BASIC,
		2: INTERIOR_STANDARD,
		3: INTERIOR_UNCOMMON,
		4: INTERIOR_ADVANCED,
	}
	return difficultyMap[difficulty]

def getOccupant(floor, difficulty):
	occupant = getOccupantsFromDifficulty(difficulty)[floor.occupancy - (3 if difficulty else 1)]
	return occupant

def printLegendRecursive(floor, difficulty):
	occupant = getOccupant(floor, difficulty)
	print(f"{occupant[1]}: {occupant[0]}")
	for child in floor.childs:
		printLegendRecursive(child,difficulty)

def printLegend(floors, difficulty):
	print("Legend:")
	occupancy = INTERIOR_LOBBY
	floor = floors[0]	
	print(f"{occupancy[floor.occupancy-1][1]}: {occupancy[floor.occupancy-1][0]}")
	floor = floor.childs[0]	
	print(f"{occupancy[floor.occupancy-1][1]}: {occupancy[floor.occupancy-1][0]}")
	for child in floor.childs:
		printLegendRecursive(child,difficulty)


def on_press(key):
	if key == keyboard.Key.esc:
		# Stop listener
		global exitApp 
		exitApp = True
		return False
	if key == keyboard.Key.enter:
		# Stop listener
		input()
		return False

	else:
		return

exitApp = False
while not exitApp:
	difficulty = getDifficulty()
	all_floors = getArchitecture()
	setIDs(all_floors)
	populateFloors(all_floors)

	printArchitecture(all_floors)
	printLegend(all_floors,difficulty)

	print("Press ESC to leave, press ENTER to generate new...\n")
	with keyboard.Listener(on_press=on_press) as listener:
		listener.join()

	
