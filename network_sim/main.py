import random
import math

# defs
DEBUG = 4
INFO = 3
WARNING = 2
ERROR = 1

SUCCESS = 0
ERROR = 1

POWER = {0:-5, 1:-1, 2:1, 3:3, 4:5, 5:12, 6:14}
MILE_TO_KM = 1.609
KM_TO_TILES = 10

# config
num_of_nodes = 300
x_size = 100
y_size = 100
cluster_init_threshold = 1
new_map = True
default_power_level = 6
map_file = "map"
PRINT_LEVEL = INFO
freq_MHz = 2400
receiver_sensetivity = -89

global network

def main():
	global network
	loop = 1
	
	
	#init
	_print("Running...",INFO)

	#generate file
	network = Network(x_size, y_size, num_of_nodes)
	
	#network.map.display()
	
	######################## Protocol ###########################################
	# 1. Each node get neighbor list											#
	# 2. Each remaining orphaned node tries to assign a cluster head			#
	# 3. Each recently new cluster heads pick a cluster head assigner			#
	# 4. Any new cluster head assigners, pick a new cluster head				#
	# 5. Any remaining orphans force closest cluster head to increase power		#
	#############################################################################
	
	# 1. Each node get neighbor list
	for node in network.node_list:
		node.get_neighbors()
	
	for node in network.node_list:

		if not node.is_orphan():
			continue
		
		# 2. Each remaining orphaned node tries to assign a cluster head
		status, new_cluster_head = node.select_cluster_head()
		if (status == ERROR):
			continue
		new_cluster_head.init_cluster_head()
		
		
		while (True):
		
			# 3. New cluster heads pick a cluster head assigner	
			status, assigner = new_cluster_head.select_cluster_head_assigner()
			if (status == ERROR):
				break
				
			# 4. When assigned, cluster head assigners, pick a new cluster head			
			status, new_cluster_head = assigner.select_cluster_head()
			if (status == ERROR):
				break			
			new_cluster_head.init_cluster_head()		
			
	# 5. Any remaining orphans force closest cluster head to increase power
	_print("Remaining Orphan Assignment: ",DEBUG)
	for node in network.node_list:
		if not node.is_orphan():
			continue

		_print("Orphan:" + node.name,DEBUG)			
		while (True):
			status = node.increase_power()
			node.get_neighbors()
			if (status == ERROR):
				_print("Exceeded Max Power",DEBUG)			
				neighbor_id = node.neighbor_list.closest_neighbor_id()
				if neighbor_id == ERROR:
					_print("Orphaned",WARNING)
					break
				neighbor = network.get_node(neighbor_id)

				_print("Forcing neighbor as cluster head: " + neighbor.name,DEBUG)
				neighbor.power_level = node.power_level
				neighbor.get_neighbors()
				neighbor.force_cluster_head()
				break
			else:
				_print("Increasing Node Power",DEBUG)
			
			
			status, cluster_head = node.find_cluster_head()
			if (status == ERROR):
				_print("Couldn't find cluster head at this power level",DEBUG)
				continue
			else:
				_print("Found Cluster Head: " + cluster_head.name,DEBUG)			
				cluster_head.power_level = node.power_level
				cluster_head.get_neighbors()
				cluster_head.cluster_head.claim_children()
				break
				

	
	#network.status()
	network.print_statistics()
	

class Network:

	def __init__(self, x_size, y_size, num_of_nodes):
	
		self.node_list = []
		self.cluster_head_list = []
		
		for i in range(num_of_nodes):
			node = Node(i)
			self.node_list.append(node)
		
		self.map = Map(self.node_list)
	
			
	def get_node(self,guid):
		return self.node_list[guid]
	
	def list_nodes(self):
		for node in self.node_list:
			_print(node.info(),DEBUG)
	
	def status(self):
		print("\nNETWORK STATUS\n")
		print("Cluster Heads:")
		for node in self.node_list:
			if node.is_cluster_head():
				print node.name,", Power Level: ",node.power_level,", Children: "
				
				for child in node.cluster_head.children:
					print "\t" + child.name
		
		print("Orphans:")
		for node in self.node_list:
			if node.cluster_head.is_unassigned():
				print node.name
				
	def print_statistics(self):
		orphan_num = 0
		cluster_num = 0
		power_level_sum = 0
	
		for node in network.node_list:
			if node.is_orphan():
				orphan_num+=1
			if node.is_cluster_head():
				cluster_num+=1
			power_level_sum += math.pow(10,POWER[node.power_level]/10.0)
		nodes_per_cluster = len(network.node_list)/ float(cluster_num)
		av_power_level = float(power_level_sum) / len(network.node_list)
	
		_print("Number of Orphans: " + str(orphan_num),INFO)
		_print("Number of Clusters: " + str(cluster_num),INFO)
		_print("Nodes per Cluster: " + str(nodes_per_cluster),INFO)
		_print("Average Power Level: " + str(av_power_level), INFO)
class Map:

	def __init__(self, node_list):
	
		self.map_matrix = [[Empty() for x in range(x_size)] for y in range(y_size)]
		
		for node in node_list:
		
			if node.x == None and node.y == None:			
				while (True):
					
					x = random.randrange(x_size)
					y = random.randrange(y_size)
					if not self.map_matrix[y][x].spot_available():
						continue
					else:
						self.map_matrix[y][x] = node
						node.set_pos(y,x)
						break
			else:
				self.map_matrix[y][x] = node

	
	def display(self):
	
		print "   ",
		for ic in range(len(self.map_matrix[0])):
			print ic % 10,
		print
		
		print "   ",		
		for column in self.map_matrix[0]:
			print "-",
		print 
		
		j = 0
		for row in self.map_matrix:
			print j % 10,
			print "|",
			j+=1
			for node in row:
				print node.display(),
			print
	

	
class Node:

	def __init__(self,guid):
		self.guid = guid
		self.char = chr((self.guid % 93) + 48)
		self.cluster_head = Unassigned()
		self.x = None
		self.y = None	
		self.power_level = default_power_level
		self.neighbor_list = None
		
	def display(self):
		if self.is_cluster_head() or False:
			return self.char
		elif self.cluster_head.is_unassigned():
			return self.char
		else:	
			return self.cluster_head.char
		
	def max_distance(self):
		path_loss_threshold = POWER[self.power_level] + receiver_sensetivity * -1
		return int(math.pow(10,(path_loss_threshold - 35.56)/20)/freq_MHz * MILE_TO_KM * KM_TO_TILES)
	
	@property
	def name(self):
		return "Node " + str(self.char) + " (00" + str(self.guid) + ")"
	
	def increase_power(self):
		if self.power_level >= 6:
			return ERROR
		else:
			self.power_level+=1
			return SUCCESS
	
	def set_pos(self,y,x):
		self.x = x
		self.y = y
	
	def spot_available(self):
		return False		
	
	def info(self):
		return "Node " + self.char \
		+ ": GUID=" + str(self.guid) \
		+ ", x=" + str(self.x) \
		+ ", y=" + str(self.y)

	def status(self):
		return "Node " + self.char \
		+ ": GUID=" + str(self.guid) \
		+ ", neighbors" + str(len(neighbor_list)) \
		+ ", CH=" + str(self.cluster_head.status)
		
	def get_neighbors(self):
		#global network
		self.neighbor_list = NeighborList()
		
		for other in network.node_list:
			if other == self:
				continue
		
			dist = self.calc_distance(other)
			if (dist < self.max_distance()):
				self.neighbor_list.add(other.guid,dist)
					
	def calc_distance(self,other):
		x_dist = self.x - other.x
		y_dist = self.y - other.y
		dist = math.sqrt(math.pow(x_dist,2) + math.pow(y_dist,2))
		return dist
	
	def is_unassigned(self):
		return False
	
	def is_cluster_head(self):
		return self.cluster_head.__class__.__name__ == "ClusterHead"
	
	def is_orphan(self):
		return self.cluster_head.__class__.__name__ == "Unassigned"
	
	def init_cluster_head(self):
		self.cluster_head = ClusterHead(self)
	
	def assign(self, cluster_head):
		self.cluster_head = cluster_head
	
	def select_cluster_head(self):
		
		_print("Selecting new cluster head...",DEBUG)
		new_cluster_head = None
		for neighbor in self.neighbor_list.list:
			node = network.get_node(neighbor.guid)		
			if node.cluster_head.is_unassigned():
				new_cluster_head = node
				break
				
		if new_cluster_head == None:
			return ERROR, None
			
		for neighbor in self.neighbor_list.list:
			node = network.get_node(neighbor.guid)
			if node.cluster_head.is_unassigned():
				if node.neighbor_list.unassigned_neighbors > new_cluster_head.neighbor_list.unassigned_neighbors:
					new_cluster_head = node
		
		if new_cluster_head.neighbor_list.unassigned_neighbors < cluster_init_threshold:
			return ERROR, None
		
		_print(new_cluster_head.name + ", Unassigned Neighbors=" + str(new_cluster_head.neighbor_list.unassigned_neighbors),DEBUG)
		return SUCCESS, new_cluster_head
	
	def select_cluster_head_assigner(self):
		_print("Selecting new cluster head assigner...",DEBUG)
		if not self.cluster_head.children:
			return ERROR, None
			
		new_cluster_head = self.cluster_head.children[0]
		
		for node in self.cluster_head.children[1:]:
			if node.cluster_head.is_unassigned():
				if node.neighbor_list.unassigned_neighbors > new_cluster_head.neighbor_list.unassigned_neighbors:
					new_cluster_head = node
		_print(new_cluster_head.name + ", Unassigned Neighbors=" + str(new_cluster_head.neighbor_list.unassigned_neighbors),DEBUG)				
		return SUCCESS, new_cluster_head	
	
	def select_cluster_head_assigner_rand(self):
		_print("Selecting new cluster head assigner...",DEBUG)
		if not self.cluster_head.children:
			return ERROR, None
		
		range = len(self.cluster_head.children[1:])
		rand = random.randrange(range)
		new_cluster_head = self.cluster_head.children[rand]
		return SUCCESS, new_cluster_head	
		
	def find_cluster_head(self):
		for neighbor in self.neighbor_list.list:
			
			node = network.get_node(neighbor.guid)			
			if node.is_cluster_head():
				return SUCCESS, node
			else:
				_print("Neighbor: " + node.name,DEBUG)
		return ERROR, None
	
	def force_cluster_head(self):

		if not self.is_orphan():

			self.cluster_head.cluster_head.children.remove(self)
		self.init_cluster_head()
		
	
class Empty:

	def __init__(self):
		pass
		
	def spot_available(self):
		return True
		
	def display(self):
		return " "

class Neighbor:

	def __init__(self,guid,distance):
		self.guid = guid
		self.distance = distance

class NeighborList:

	def __init__(self):
		self.list = []
		
	def add(self,guid,distance):
		self.list.append(Neighbor(guid,distance))
	
	@property
	def length(self):
		return len(self.list)
		
	@property
	def unassigned_neighbors(self):
		num = 0
		for neighbor in self.list:
			if network.get_node(neighbor.guid).cluster_head.is_unassigned():
				num+=1
		return num
	
	def closest_neighbor_id(self):
		if not self.list:
			return ERROR
		min_dist_neighbor = self.list[0]
		for neighbor in self.list[1:]:
			if min_dist_neighbor.distance > neighbor.distance:
				min_dist_neighbor = neighbor
		return min_dist_neighbor.guid
			
	
class ClusterHead:

	def __init__(self, node):
		self.node = node
		self.children = []
		_print("New Cluster Head: " + self.node.name, DEBUG)		
		self.claim_children()
		
	def is_unassigned(self):
		return False				
	
	def status(self):
		return "Yes"
	
	def claim_children(self):
		_print("Claiming Children...", DEBUG)
				
		for neighbor in self.node.neighbor_list.list:
			node = network.get_node(neighbor.guid)
			if node.cluster_head.is_unassigned():
				_print(node.name, DEBUG)
				self.children.append(node)
				node.assign(self.node)
				node.power_level = self.node.power_level
				node.get_neighbors()
				
class Unassigned:

	def __init__(self):
		pass

	def is_unassigned(self):
		return True
		
	def status(self):
		return "Unassigned"
	
def _print(string,level):
	global PRINT_LEVEL
	
	if not level <= PRINT_LEVEL:
		pass
	else:
		if (level == DEBUG):
			print("[DEBUG] " + str(string))
		elif (level == INFO):
			print("[INFO] " + str(string))
		elif (level == WARNING):
			print("[WARNING] " + str(string))		
		elif (level == ERROR):
			print("[ERROR] " + str(string))
			quit()
		else:
			pass


main()