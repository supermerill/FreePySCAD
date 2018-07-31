#########################################################
# This file is distributed against the LGPL licence     #
# This file is made by supermerill (Remi Durand)        #
#########################################################

######################################
# print("You can use something like 'from ", __name__," import *' for a more convenient experience")
#
# usage: scene().show( many statement )
# if you want to make a fucntion, don't forget to return the root node!
# Each function like cube() or union() return an object (EasyNode) 
#  which store the know-how of how to build the object tree if needed.
# The scene will only redraw a node and these children if one of the 
#  child is changed. 
#
#
# move() rotate() scale() color() return a differnt kind of object
#  because they are not a mod but a modifier onto a node. They can 
#  be use almost like the other one, no ned to worry.
#
# Color, multmatrix and scale can't be applied on a node so they are
#  passed to the leafs.
#
# more info on the github wiki
######################################

import Part, FreeCAD, math, Draft, InvoluteGearFeature, importSVG, Mesh
from FreeCAD import Base

######### basic functions #########
def getColorCode(str):
	if(str == "red"):		return (1.0,0.0,0.0,0.0)
	if(str == "lime"):		return (0.0,1.0,0.0,0.0)
	if(str == "blue"):		return (0.0,0.0,1.0,0.0)
	if(str == "cyan"):		return (0.0,1.0,1.0,0.0)
	if(str == "aqua"):		return (0.0,1.0,1.0,0.0)
	if(str == "fuchsia"):	return (1.0,0.0,1.0,0.0)
	if(str == "yellow"):	return (1.0,1.0,0.0,0.0)
	if(str == "black"):		return (0.0,0.0,0.0,0.0)
	if(str == "black"):		return (0.0,0.0,0.0,0.0)
	if(str == "gray"):		return (0.5,0.5,0.5,0.0)
	if(str == "silver"):	return (.75,.75,.75,0.0)
	if(str == "white"):		return (  1,  1,  1,0.0)
	if(str == "maroon"):	return (0.5,0.0,0.0,0.0)
	if(str == "green"):		return (0.0,0.5,0.0,0.0)
	if(str == "navy"):		return (0.0,0.0,0.5,0.0)
	if(str == "teal"):		return (0.0,0.5,0.5,0.0)
	if(str == "purple"):	return (0.5,0.0,0.5,0.0)
	if(str == "olive"):		return (0.5,0.5,0.0,0.0)
	return (0.5,0.5,0.5,0.5)
	
# def getTuple3(default, *params):
	# if len(params) == 0 :
		# return (default,default,default)
	# if len(params)==1 and isinstance(params[0], list) :
			# return (float(params[0][0]) if len(params[0])>0 else default, float(params[0][1]) if len(params[0])>1 else default, float(params[0][2]) if len(params[0])>2 else default)
	# return ( float(params[0]) if len(params)>0 else default, float(params[1]) if len(params)>1 else default, float(params[2]) if len(params)>2 else default )

# def getTuple4(default, *params):
	# if len(params) == 0 :
		# return (default,default,default,default)
	# if len(params)==1 and isinstance(params[0], list) :
			# return (float(params[0][0]) if len(params[0])>0 else default, float(params[0][1]) if len(params[0])>1 else default, float(params[0][2]) if len(params[0])>2 else default, float(params[0][3]) if len(params[0])>3 else default)
	# return ( float(params[0]) if len(params)>0 else default, float(params[1]) if len(params)>1 else default, float(params[2]) if len(params)>2 else default, float(params[3]) if len(params)>3 else default )

def getTuple2(a,b,default_first_item):
	if(isinstance(a, list)):
		if(len(a)==0):
			a=default_first_item
		elif(len(a)==1):
			a=a[0]
		elif(len(a)==2):
			b=a[1]
			a=a[0]
	return (a,b)
def getTuple2Abs(a,b,default_first_item):
	(a,b) = getTuple2(a,b,default_first_item)
	return (abs(a), abs(b))
def getTuple3(a,b,c,default_first_item):
	if(isinstance(a, list)):
		if(len(a)==0):
			a=default_first_item
		elif(len(a)==1):
			a=a[0]
		elif(len(a)==2):
			b=a[1]
			a=a[0]
		elif(len(a)==3):
			c=a[2]
			b=a[1]
			a=a[0]
	return (a,b,c)
def getTuple3Abs(a,b,c,default_first_item):
	(a,b,c) = getTuple3(a,b,c,default_first_item)
	return (abs(a),abs(b),abs(c))
def getTuple4(a,b,c,d,default_first_item):
	if(isinstance(a, list)):
		if(len(a)==0):
			a=default_first_item
		elif(len(a)==1):
			a=a[0]
		elif(len(a)==2):
			b=a[1]
			a=a[0]
		elif(len(a)==3):
			c=a[2]
			b=a[1]
			a=a[0]
		elif(len(a)==4):
			d=a[3]
			c=a[2]
			b=a[1]
			a=a[0]
	return (a,b,c,d)
def getTuple4Abs(a,b,c,d,default_first_item):
	(a,b,c,d) = getTuple4(a,b,c,d,default_first_item)
	return (abs(a),abs(b),abs(c),abs(d))
	
######### scene class #########

if(not 'tree_storage' in globals()):
	global tree_storage
	tree_storage = {}

class Scene:
	def __init__(self):
		doc = FreeCAD.ActiveDocument
	def draw(self, *tupleOfNodes):
		global tree_storage
		try:
			if(not FreeCAD.ActiveDocument in tree_storage):
				tree_storage[FreeCAD.ActiveDocument] = []
			keep_nodes = []
			i=0
			doc = FreeCAD.ActiveDocument
			newArrayOfNodes = []
			# This algo can't support a shuffle (or insert) of new object in the root.
			# But it works
			for node_idx in range(len(tupleOfNodes)):
				if(len(tree_storage[FreeCAD.ActiveDocument])<=node_idx):
					newArrayOfNodes.append(tupleOfNodes[node_idx].create())
				else:
					newArrayOfNodes.append(tupleOfNodes[node_idx].check(doc, tree_storage[FreeCAD.ActiveDocument][node_idx]))
				node_idx+=1
			if(len(tree_storage[FreeCAD.ActiveDocument])>len(tupleOfNodes)):
				for node_idx in range(len(tupleOfNodes), len(tree_storage[FreeCAD.ActiveDocument])):
					tree_storage[FreeCAD.ActiveDocument][node_idx].destroyObj(doc)
		except:
			print("Unexpected error:")
		# if True:
			tree_storage[FreeCAD.ActiveDocument] = []
			for obj in doc.Objects :
				doc.removeObject(obj.Name)
			FreeCAD.ActiveDocument.recompute()
			raise
		tree_storage[FreeCAD.ActiveDocument] = tuple(newArrayOfNodes)
		FreeCAD.ActiveDocument.recompute()
		return self;
	def __call__(self, *tupleOfNodes):
		return self.draw(*tupleOfNodes)

def scene():
	return Scene()

######### Basic class a utilities ######### 

_idx_EasyNode = 0

class EasyNode:
	def __init__(self):
		self.childs = []
		self.actions = []
		self.actions_after = []
		self.simple = True
	def addAction(self, method, args):
		self.actions.append((method,args))
	def __hash__(self):
		if(hasattr(self, '_hash')):
			if(self._hash):
				return 0
			else:
				self._hash = True
		else:
			self._hash = True
		hashval = 0
		i=0
		for action in self.actions:
			# print("action="+str(action))
			hashval = hashval + (hash(action[0].__name__))
			i+=517
			for arg in action[1]:
				if(isinstance(arg, EasyNode) or isinstance(arg, tuple) or isinstance(arg, list)):
					temp = 0
				else:
					temp = (hash(arg)*i)
				hashval = (hashval+temp) if temp<10000 else hashval ^ temp
				i+=317
		return hashval
	def printhash(self):
		hashval = 0
		i=0
		for action in self.actions:
			hashval = hashval + (hash(action[0].__name__))
			print("hash of act "+action[0].__name__+" = ",str(hash(action[0].__name__))+" => "+str(hashval))
			i+=517
			
			for arg in action[1]:
				print(isinstance(arg,EasyNode))
			for arg in action[1]:
				# print("arg : "+str(arg)+" "+str( isinstance(arg, EasyNode)))
				# try:
					# print(dir(arg))
				# except:
					# print("not a class")
				if(isinstance(arg, EasyNode) or isinstance(arg, tuple)):
					temp = 0
					print("arg passed")
				else:
					temp = (hash(arg)*i)
					hashval = (hashval+temp) if temp<10000 else hashval ^ temp
					print("hash of arg "+str(arg)+" = "+str(temp*i)+" => "+str(hashval))
				i+=317
		print("final => "+str(hashval))
		return hashval
	def hashWhithChilds(self):
		hashval = hash(self)
		i=0;
		for child in self.childs:
			hashval = hashval ^ (child.hashWhithChilds()*i)
			i+=317
		return hashval
	def create(self):
		for action in self.actions :
			action[0](*action[1])
		for action in self.actions_after :
			action[0](*action[1])
		return self
	def destroyObj(self, doc):
		if(hasattr(self,'obj')):
			print("destroy "+self.obj.Name)
			doc.removeObject(self.obj.Name)
		for child in self.childs:
			child.destroyObj(doc)
	# return the node to use
	def check(self, doc, clone):
		print("check "+self.name)
		ok = True
		if(self.simple):
			#must be done before, to update things?
			hash(self)
			hash(clone)
			if(hash(self) == hash(clone) and len(self.childs) == len(clone.childs)):
				i=0
				for item in self.childs:
					print(hash(self.childs[i])," == ",hash(clone.childs[i]))
					ok = ok and hash(self.childs[i]) == hash(clone.childs[i])
					# if(not hash(self.childs[i]) == hash(clone.childs[i])):
						# self.childs[i].printhash()
						# clone.childs[i].printhash();
						
					i+=1
				print("simple, same hash and childs are ",ok)
				# print(hash(self)," == ",hash(clone))
				# self.printhash()
				# clone.printhash();
			else:
				ok = False
				print("simple but hash: ",hash(self)," != ",hash(clone),hash(self)==hash(clone)," or ",len(self.childs)," != ",len(clone.childs),len(self.childs)==len(clone.childs))
		else:
			ok = (self.hashWhithChilds() == clone.hashWhithChilds())
			print("it's complicated ",ok)
		if(ok):					
			print("keep "+clone.name+" and ditch "+self.name)
			#ok, do not modify it but check the childs
			self.obj = clone.obj
			newNodes = []
			i=0
			ok = True
			for child in self.childs:
				good = self.childs[i].check(doc, clone.childs[i])
				print("use the new one in the old coll? "+str(good == self.childs[i])+" ( "+str(good)+" =?= "+str(self.childs[i]))
				if(not good == clone.childs[i]):
					clone.childs[i] = good
					ok = False
				i+=1
			if(not ok):
				print("reflow "+clone.name)
				clone.clear_childs().layout_childs(*tuple(clone.childs))
			return clone
		else:
			print("recreate "+self.name)
			# redo everything
			clone.destroyObj(doc)
			self.create()
			return self

	def add(self, *tupleOfNodes):
		if(len(tupleOfNodes)==1 and (isinstance(tupleOfNodes[0], list) or isinstance(tupleOfNodes[0], tuple))):
			tupleOfNodes = tuple(tupleOfNodes[0])
		for enode in tupleOfNodes :
			if(isinstance(enode, EasyNode)):
				self.childs.append(enode)
			else:
				print("error, trying to add '"+str(enode)+"' into a union of EsayNode")
		self.actions.append((self.create_childs,tupleOfNodes))
		self.actions.append((self.layout_childs,tupleOfNodes))
		return self
	def __call__(self, *tupleOfNodes):
		return self.add(*tupleOfNodes)
	def create_childs(self, *tupleOfNodes):
		for enode in tupleOfNodes :
			if(isinstance(enode, EasyNode)):
				enode.create()
	def layout_childs(self, *tupleOfNodes):
		arrayShape = self.obj.Shapes
		for enode in tupleOfNodes :
			if(isinstance(enode, EasyNode)):
				arrayShape.append(enode.obj)
				enode.obj.ViewObject.Visibility = False
			else:
				print("error, trying to layout '"+str(enode)+"' into a union of EsayNode")
		self.obj.Shapes = arrayShape
		return self
	def clear_childs(self, *tupleOfNodes):
		self.obj.Shapes = []
		return self
	# def printmyargs(self, *args):
		# print(args)
	def translate(self, x=0,y=0,z=0):
		return move(x,y,z)
	def move(self, x=0,y=0,z=0):
		self.actions.append((self.move_action,(x,y,z)))
		return self
	def move_action(self, x=0,y=0,z=0):
		(x,y,z) = getTuple3(x,y,z,0)
		self.obj.Placement.move(Base.Vector(x, y, z))
		return self
	def rotate(self, x=0,y=0,z=0):
		self.actions.append((self.rotate_action,(x,y,z)))
		return self
	def rotate_action(self, x=0,y=0,z=0):
		(x,y,z) = getTuple3(x,y,z,0)
		myMat = Base.Matrix()
		myMat.rotateX(x*math.pi/180)
		myMat.rotateY(y*math.pi/180)
		myMat.rotateZ(z*math.pi/180)
		self.obj.Placement=FreeCAD.Placement(myMat).multiply(self.obj.Placement)
		return self
	def scale(self, x=0,y=0,z=0):
		self.actions_after.append((self.scale_action,(x,y,z)))
		self.simple = False
		return self
	def scale_action(self, x=0,y=0,z=0):
		for node in self.childs:
			node.scale(x,y,z,_instantly=True)
		return self
	def multmatrix(self, mat):
		for node in self.childs:
			node.multmatrix(mat)
		self.simple = False
		return self
	def color(self, r=0.0,v=0.0,b=0,a=0.0,_instantly=False):
		self.actions_after.append((self.color_action,(r,v,b,a)))
		self.simple= False
		return self
	def color_action(self, r=0.0,v=0.0,b=0,a=0.0):
		for node in self.childs:
			node.color(r,v,b,a,_instantly=True)
		self.simple = False
		return self
	def x(self):
		self.actions.append((self.xyz_action,(1,0,0)))
		return self
	def y(self):
		self.actions.append((self.xyz_action,(0,1,0)))
		return self
	def z(self):
		self.actions.append((self.xyz_action,(0,0,1)))
		return self
	def xy(self):
		self.actions.append((self.xyz_action,(1,1,0)))
		return self
	def xz(self):
		self.actions.append((self.xyz_action,(1,0,1)))
		return self
	def yz(self):
		self.actions.append((self.xyz_action,(0,1,1)))
		return self
	def xyz(self):
		self.actions.append((self.xyz_action,(1,1,1)))
		return self
	def xyz_action(self,x,y,z):
		self.move_action(-self.centerx*x,-self.centery*y,-self.centerz*z)
		return self
	def center(self):
		self.actions.append((self.center_action,(1,1,1)))
		return self
	def center_action(self,x,y,z):
		self.move_action(-self.centerx if self.centerx>0 else 0.0,-self.centery if self.centery>0 else 0.0,-self.centerz if self.centerz>0 else 0.0)
		return self
		
def useCenter(node, center):
	if(center != None and callable(center)):
		center(node)
	elif(center != None and isinstance(center, bool) and center):
		node.center()

class EasyNodeColored(EasyNode):
	def color(self, r=0.0,v=0.0,b=0.0,a=0.0,_instantly=False):
		if isinstance(r, str):
			if(a!=0.0):
				colorcode = getColorCode(r)
				colorcode[3] = a
				if(_instantly):
					self.color_action(colorcode)
				else:
					self.actions.append((self.color_action,(colorcode,)))
			else:
				if(_instantly):
					self.color_action(getColorCode(r))
				else:
					self.actions.append((self.color_action,(getColorCode(r),)))
		else:
			#fixme: try to see in an array is not hidden inside the r
			(r,v,b,a) = getTuple4Abs(r,v,b,a,0.0)
			if(_instantly):
				self.color_action((max(0.0,min(r,1.0)),max(0.0,min(v,1.0)),max(0.0,min(b,1.0)),max(0.0,min(a,1.0))))
			else:
				self.actions.append((self.color_action,((max(0.0,min(r,1.0)),max(0.0,min(v,1.0)),max(0.0,min(b,1.0)),max(0.0,min(a,1.0))),)))
		return self
	def color_action(self, colorcode):
		self.obj.ViewObject.DiffuseColor = [colorcode]
		return self
def magic_color(node, r=0.0,v=0.0,b=0.0,a=0.0):
		node.color(r,v,b,a)
		return node

class EasyNodeLeaf(EasyNodeColored):
	# def __init__(self):
		# self.childs = []
		# self.actions = []
		# self.actions_after = []
		# self.simple = True
		# self.centerx=0.0
		# self.centery=0.0
		# self.centerz=0.0
	def scale(self, x=0.0,y=0.0,z=0,_instantly=False):
		if(_instantly):
			self.scale_action(x,y,z)
		else:
			self.actions.append((self.scale_action,(x,y,z)))
		return self
	def scale_action(self, x,y,z):
		(x,y,z) = getTuple3(x,y,z,0.0)
		myMat = Base.Matrix()
		myMat.scale(x,y,z)
		self.obj.Shape = self.obj.Shape.transformGeometry(myMat)
		return self
	def multmatrix(self, mat):
		flatarray = []
		for array in mat:
			for num in array:
				flatarray.append(num)
		if matsize != len(flatarray):
			print("error, wrong matrix")
		else:
			myMat = Base.Matrix()
			myMat.A = flatarray
			self.obj.Shape = self.obj.Shape.transformGeometry(myMat)
		return self
		
# def import_)

######### transformations ######### 

def union(name=None):
	global _idx_EasyNode
	node = EasyNode()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "union_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createUnion(node,name):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "union_"+str(_idx_EasyNode))
	node.addAction(createUnion, (node,name))
	return node
	
def inter(name=None):
	global _idx_EasyNode
	node = EasyNode()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "inter_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createInter(node,name):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::MultiCommon", "inter_"+str(_idx_EasyNode))
	node.addAction(createInter, (node,name))
	return node

class EasyNodeDiff(EasyNode):
	def __init__(self):
		self.my_union = None
		self.unionChilds = []
		self.childs = []
		self.actions = []
		self.actions_after = []
		self.simple = True
	def add(self, *tupleOfNodes):
		if(len(tupleOfNodes)==1 and (isinstance(tupleOfNodes[0], list) or isinstance(tupleOfNodes[0], tuple))):
			tupleOfNodes = tuple(tupleOfNodes[0])
		good_array = []
		minidx = 0
		newunion = False
		for enode in tupleOfNodes :
			if(isinstance(enode, EasyNode)):
				good_array.append(enode)
		if(len(good_array)==0):
			return self
		if(len(self.childs)==2 and len(self.childs[1].childs)>1):
			# simple case: give them to the union
			for enode in good_array :
				self.childs.append(enode)
				self.unionChilds.append(enode)
		elif( (len(self.childs)<2 or len(self.childs[1].childs)==0) and len(self.childs)+len(good_array)>2):
			# create the union
			self.my_union = union()
			newunion = True
			self.unionChilds = []
			temp = None
			if(len(self.childs)==0):
				self.childs.append(good_array[minidx])
				minidx+=1
			if(len(self.childs)==1):
				self.childs.append(self.my_union)
			else:
				self.unionChilds.append(self.childs[1])
				self.childs[1] = self.my_union
				self.childs.append(self.unionChilds[0])
			for enode in good_array[minidx:] :
				self.childs.append(enode)
				self.unionChilds.append(enode)
		else:
			# just use them
			if(len(self.childs)==0 and len(good_array)>0):
				self.childs.append(good_array[minidx])
				minidx+=1
			if(len(self.childs)==1 and len(good_array)>0):
				self.childs.append(good_array[minidx])
				minidx+=1
			
		if(newunion):
			self.actions.append((self.create_childs,(self.my_union,)+tuple(good_array)))
		else:
			self.actions.append((self.create_childs,tuple(good_array)))
		self.actions.append((self.layout_childs,tuple(good_array)))
		return self
	def layout_childs(self, *tupleOfNodes):
		if(self.obj.Base == None and len(tupleOfNodes)>0):
			self.obj.Base = tupleOfNodes[0].obj
			tupleOfNodes[0].obj.ViewObject.Visibility = False
			tupleOfNodes = tupleOfNodes[1:]
		if(self.my_union == None and self.obj.Tool == None and len(tupleOfNodes)>0):
			self.obj.Tool = tupleOfNodes[0].obj
			tupleOfNodes[0].obj.ViewObject.Visibility = False
			tupleOfNodes = tupleOfNodes[1:]
		if(self.my_union != None and len(tupleOfNodes)>0):
			self.obj.Tool = self.my_union.obj
			self.my_union.layout_childs(*tupleOfNodes)
		return self

def cut(name=None):
	global _idx_EasyNode
	node = EasyNodeDiff()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "cut_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createCut(node,name):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Cut", node.name)
		node.obj.Base = None
		node.obj.Tool = None
	node.addAction(createCut, (node,name))
	return node
def difference(name=None):
	return cut(name)

# FIXME: The color doesn't apply to the chamfered/fillet section
class EasyNodeChamfer(EasyNode):
	def __init__(self):
		self.edges = [];
		self.childs = []
		self.actions = []
		self.actions_after = []
		self.simple = True
	def layout_childs(self, *tupleOfNodes):
		if(len(tupleOfNodes)>0):
			self.obj.Base = tupleOfNodes[0].obj
			self.obj.Base.ViewObject.Visibility = False
			self.obj.Edges = self.edges
		return self
	def set(self, node):
		self.add(node)
		return self
	def addEdge(self, length, *arrayOfEdges):
		if isinstance(length, list):
			if len(length) == 2:
				self.addEdge2(length[0],length[1],*arrayOfEdges)
			else:
				self.addEdge2(length[0],length[0],*arrayOfEdges)
		else:
			self.addEdge2(length,length,*arrayOfEdges)
		return self
	def addEdge2(self, startLength, endLength, *arrayOfEdges):
		for eidx in arrayOfEdges :
			self.edges.append((eidx, startLength, endLength))
		# self.obj.Edges = self.edges
		return self
	def setNb(self, length, nb, node):
		self.set(node)
		for eidx in range(1, nb+1) :
			self.edges.append((eidx, length, length))
		# self.obj.Edges = self.edges
		return self

def chamfer(name=None):
	global _idx_EasyNode
	node = EasyNodeChamfer()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "chamfer_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createChamfer(node):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Chamfer", node.name)
	node.addAction(createChamfer, (node,))
	return node

def fillet(name=None):
	global _idx_EasyNode
	node = EasyNodeChamfer()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "fillet_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createFillet(node):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Fillet", node.name)
	node.addAction(createFillet, (node,))
	return node

class EasyNodeMirror(EasyNodeColored):
	def __init__(self):
		self.edges = [];
		self.childs = []
		self.actions = []
		self.actions_after = []
		self.simple = True
	def layout_childs(self, *tupleOfNodes):
		if(len(tupleOfNodes)>0):
			self.obj.Source = tupleOfNodes[0].obj
			self.obj.Source.ViewObject.Visibility = False
		return self

def mirror(x=0.0,y=0.0,z=0.0,name=None):
	(x,y,z) = getTuple3(x,y,z,0.0)
	global _idx_EasyNode
	node = EasyNodeMirror()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "mirror_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createMirror(node):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Mirroring", node.name)
		node.obj.Base = Base.Vector(0,0,0)
		node.obj.Normal = Base.Vector(x,y,z).normalize()
	node.addAction(createMirror, (node))
	return node

def offset(length=1.0,fillet=True,fusion=True,name=None):
	global _idx_EasyNode
	node = EasyNodeMirror()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "offset_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createOffset(node, length, fillet, fusion):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Offset", node.name)
		node.obj.Value = length
		node.obj.Mode = 0
		node.obj.Join = 0 if(fillet) else 2
		node.obj.Intersection = fusion
		node.obj.SelfIntersection = False
	node.addAction(createOffset, (node, length, fillet, fusion))
	return node

def offset2D(length=1.0,fillet=True,fusion=True,name=None):
	global _idx_EasyNode
	node = EasyNodeMirror()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "offset2D_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createOffset2D(node, length, fillet, fusion):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Offset2D", node.name)
		node.obj.Value = length
		node.obj.Mode = 0
		node.obj.Join = 0 if(fillet) else 2
		node.obj.Intersection = fusion
		node.obj.SelfIntersection = False
	node.addAction(createOffset2D, (node, length, fillet, fusion))
	return node

######### 3D objects ######### 


def cube(size=0.0,y=0.0,z=0.0,center=None,x=0.0, name=None):
	(x,y,z,size) = getTuple4Abs(size,y,z,x,0.0)
	if(x==0.0 and size != 0.0):
		x = size
	if(y==0.0 and z==0.0):
		return box(x,x,x,center, name)
	else:
		return box(x,y if y!=0.0 else 1.0, z if z!=0.0 else 1.0,center, name)

def box(x=1.0,y=1.0,z=1.0,center=None, name=None):
	(x,y,z) = getTuple3Abs(x,y,z,1.0)
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "cube_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createBox(node, x,y,z,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makeBox(x, y, z)
		node.centerx = x/2.0
		node.centery = y/2.0
		node.centerz = z/2.0
		useCenter(node, center)
	node.addAction(createBox, (node, x,y,z,center))
	return node

def tri_rect(x=1.0,y=1.0,z=1.0,center=None, name=None):
	(x,y,z) = getTuple3Abs(x,y,z,1.0)
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "tri_rect_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createTriRect(node, x,y,z,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		poly = Part.makePolygon([Base.Vector(0,0,0),Base.Vector(x,0,0),Base.Vector(0,y,0),Base.Vector(0,0,0)]) 
		node.obj.Shape = Part.Face(poly).extrude(Base.Vector(0,0,z))
		node.centerx = x/2.0
		node.centery = y/2.0
		node.centerz = z/2.0
		useCenter(node, center)
	node.addAction(createTriRect, (node, x,y,z,center))
	return node

def cylinder(r=0.0,h=1.0,center=None,d=0.0,r1=0.0,r2=0.0,d1=0.0,d2=0.0,angle=360.0,fn=1,name=None):
	r = abs(r)
	h = abs(h)
	d = abs(d)
	if( r == 0.0 and d != 0.0):
		r = d/2.0
	if(r == 0.0 and (r1!=0.0 or r2!=0.0 or d1!=0.0 or d2!=0.0)):
		return cone(r1,r2,h,center,d1,d2,fn)
	if(fn>2):
		return poly_ext(r,fn,center)
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "cylinder_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createCylinder(node, r,h,center,angle):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		if(int(angle) == 360):
			node.obj.Shape = Part.makeCylinder(r,h)
		else:
			node.obj.Shape = Part.makeCylinder(r,h,Base.Vector(0,0,0),Base.Vector(0,0,1),angle)
		node.centerx = -r
		node.centery = -r
		node.centerz = h/2.0
		useCenter(node, center)
	node.addAction(createCylinder, (node, r,h,center,angle))
	return node

def cone(r1=1.0,r2=1.0,h=1.0,center=None,d1=0.0,d2=0.0,fn=1,name=None):
	r1 = abs(r1)
	r2 = abs(r2)
	h = abs(h)
	d1 = abs(d1)
	if( r1 == 0.0 and d1 != 0.0):
		r1 = d1/2.0
	d2 = abs(d2)
	if( r2 == 0.0 and d2 != 0.0):
		r2 = d2/2.0
	print("cone: "+str(r1)+" "+str(r2)+" "+str(h)+" "+str(fn)+" ")
	if(fn>2):
		#compute extrusion angle
		angle = 0.0
		if(r1>r2):
			angle = -math.atan(float(r1-r2)/float(h))
		else:
			angle = math.atan(float(r2-r1)/float(h))
		print(str(r1)+" "+str(fn)+" "+str(angle))
		return z_extrude(length=h,angle=angle)(poly_reg(r1,fn,center=center))
		# return poly_reg(r1,fn,center=center)
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "cone_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createCone(node, r1,r2,h,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makeCone(r1,r2,h)
		node.centerx = -r1 if r1>r2 else -r2
		node.centery = -r1 if r1>r2 else -r2
		node.centerz = h/2.0
		useCenter(node, center)
	node.addAction(createCone, (node, r1,r2,h,center))
	return node

def sphere(r=1.0,center=None,d=0.0,fn=1,name=None):
	r = abs(r)
	d = abs(d)
	if( r == 0.0 and d != 0.0):
		r = d/2.0
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "sphere_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createSphere(node, r,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makeSphere(r)
		node.centerx = -r
		node.centery = -r
		node.centerz = -r
		useCenter(node, center)
	node.addAction(createSphere, (node, r,center))
	return node

def torus(r1=1.0, r2=0.1,center=None,d1=0.0,d2=0.0,name=None):
	r1 = abs(r1)
	r2 = abs(r2)
	d1 = abs(d1)
	if( r1 == 0.0 and d1 != 0.0):
		r1 = d1/2.0
	d2 = abs(d2)
	if( r2 == 0.0 and d2 != 0.0):
		r2 = d2/2.0
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "torus_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createTorus(node, r1,r2,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makeTorus(r1, r2)
		node.centerx = -r1
		node.centery = -r1
		node.centerz = -r2
		useCenter(node, center)
	node.addAction(createTorus, (node, r1,r2,center))
	return node
	

def poly_ext(r=1.0, nb=3, h=1.0,center=None,d=0.0,name=None):
	r = abs(r)
	h = abs(h)
	nb= max(3, abs(nb))
	d = abs(d)
	if( r == 0.0 and d != 0.0):
		r = d/2.0
	global _idx_EasyNode
	node = EasyNodeLeaf()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "3Dpolygon_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createPolyExt(node, r,nb,h,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		# create polygon
		points = [Base.Vector(r,0,0)]
		for i in range(1,nb):
			points.append(Base.Vector(r * math.cos(2*math.pi*i/nb), r * math.sin(2*math.pi*i/nb),0))
		points.append(Base.Vector(r,0,0))
		temp_poly = Part.makePolygon(points) 
		node.obj.Shape = Part.Face(temp_poly).extrude(Base.Vector(0,0,h))
		# pol = Draft.makePolygon(nb,radius=r,inscribed=True,face=True,support=None)
		# node.obj.Shape = Part.Face(pol).extrude(Base.Vector(0,0,h))
		node.centerx = -r
		node.centery = -r
		node.centerz = h/2.0
		useCenter(node, center)
	node.addAction(createPolyExt, (node, r,nb,h,center))
	return node

def poly_int(a=1.0, nb=3, h=1.0,center=None,d=0.0,name=None):
	a = abs(a)
	h = abs(h)
	nb= max(3, abs(nb))
	d = abs(d)
	if( a == 0.0 and d != 0.0):
		a = d/2.0
	# create polygon with apothem, not radius
	radius = a * math.cos(math.radians(180)/nb)
	return poly_ext(radius,nb,h,center,name)

######### 2D & 1D objects ######### 

class EasyNode2D(EasyNodeLeaf):
	def __init__(self):
		# super().__init__()
		centerz = 0.0
		self.childs = []
		self.actions = []
		self.actions_after = []
		self.simple = True
	def rotate2D(self, x=0.0,y=0.0):
		(x,y) = getTuple2(x,y,0.0)
		myMat = Base.Matrix()
		myMat.rotateX(y*math.pi/180)
		myMat.rotateY(x*math.pi/180)
		myMat.rotateZ(0.0)
		self.obj.Placement=FreeCAD.Placement(myMat).multiply(self.obj.Placement)
		return self

def circle(r=1.0,center=None,d=0.0,fn=1,name=None):
	r=abs(r)
	d = abs(d)
	if(fn>2):
		return poly_reg(r,fn,center)
	if( r == 0.0 and d != 0.0):
		r = d/2.0
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "circle_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createCircle(node, r,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		temp_poly = Part.makeCircle(r)
		node.obj.Shape = temp_poly
		node.centerx = -r
		node.centery = -r
		useCenter(node, center)
	node.addAction(createCircle, (node, r,center))
	return node

def ellipse(r1=0.0,r2=0.0,center=None,d1=0.0,d2=0.0,name=None):
	r1 = abs(r1)
	r2 = abs(r2)
	d1 = abs(d1)
	d2 = abs(d2)
	if( r1 == 0.0 and d1 != 0.0):
		r1 = d1/2.0
	if( r2 == 0.0 and d2 != 0.0):
		r2 = d2/2.0
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "ellipse_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createEllipse(node, r1,r2,center):
		# node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", "circle_"+str(_idx_EasyNode))
		node.obj = Draft.makeEllipse(r2,r1)
		node.obj.Label = node.name
		# node.obj.Shape = temp_poly
		node.centerx = -r2
		node.centery = -r1
		useCenter(node, center)
	node.addAction(createEllipse, (node, r1,r2,center))
	return node

def poly_reg(r=1.0,nb=3,center=None,inscr=True,d=0.0,name=None):
	r=abs(r)
	d = abs(d)
	nb=max(3,abs(nb))
	if( r == 0.0 and d != 0.0):
		r = d/2.0
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "reg_ploygon_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createPolygonReg(node, r,nb,center,inscr):
		node.obj = Draft.makePolygon(nb,radius=r,inscribed=inscr,face=True,support=None)
		node.obj.Label = node.name
		# temp_poly = Part.makeCircle(r)
		# node.obj.Shape = temp_poly
		node.centerx = -r
		node.centery = -r
		useCenter(node, center)
	node.addAction(createPolygonReg, (node, r,nb,center,inscr))
	return node

def square(size=1.0,y=0.0,x=0.0,center=None,name=None):
	(size,y,x) = getTuple3Abs(size,y,x,1.0)
	if(y>0.0):
		if(x>0.0):
			return rectangle(x,y,center=center)
		else:
			return rectangle(size,y,center=center)
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "square_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createSquare(node, size,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makePlane(size, size)
		node.centerx = size/2.0
		node.centery = size/2.0
		useCenter(node, center)
	node.addAction(createSquare, (node, size,center))
	return node

def rectangle(x=1.0,y=1.0,center=None,name=None):
	(x,y) = getTuple2Abs(x,y,1.0)
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "rectangle_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createRectangle(node, x,y,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makePlane(x, y)
		node.centerx = x/2.0
		node.centery = y/2.0
		useCenter(node, center)
	node.addAction(createRectangle, (node, x,y,center))
	return node

def polygon(points=[], closed=True,name=None):
	if(not (isinstance(points[0], list) or isinstance(points[0], tuple)) or len(points)<2):
		return circle(1)
	if(len(points)==1 and (isinstance(points[0], list) or isinstance(points[0], tuple))):
		points = points[0]
	if len(points) < 3:
		return circle(1)
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "polygon_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createPolygon(node, points,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		vectors = []
		for point in points:
			vectors.append(Base.Vector(float(point[0]) if len(point)>0 else 0.0, float(point[1]) if len(point)>1 else 0.0, float(point[2]) if len(point)>2 else 0.0))
		if(closed):
			vectors.append(Base.Vector(float(points[0][0]) if len(points[0])>0 else 0.0, float(points[0][1]) if len(points[0])>1 else 0.0, float(points[0][2]) if len(points[0])>2 else 0.0))
		temp_poly = Part.makePolygon(vectors) 
		if(closed):
			node.obj.Shape = Part.Face(temp_poly)
		else:
			node.obj.Shape = temp_poly
		node.centerx = 0.0
		node.centery = 0.0
	node.addAction(createPolygon, (node, points,center))
	return node

def bspline(points=[], closed=False,name=None):
	if(not (isinstance(points[0], list) or isinstance(points[0], tuple)) or len(points)<2):
		return circle(1)
	if(len(points)==1 and (isinstance(points[0], list) or isinstance(points[0], tuple))):
		points = points[0]
	vectors = []
	for point in points:
		if isinstance(point, list) or isinstance(point, tuple) :
			vectors.append(FreeCAD.Vector(point[0] if len(point)>0 else 0.0, point[1] if len(point)>1 else 0.0, point[2] if len(point)>2 else 0.0))
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "bspline_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createBspline(node, vectors,center,closed):
		node.obj = Draft.makeBSpline(vectors,closed=closed,face=closed,support=None)
		node.obj.Label = node.name
		node.centerx = 0.0
		node.centery = 0.0
	node.addAction(createBspline, (node, vectors,center,closed))
	return node

def bezier(points=[], closed=False,name=None):
	if(not (isinstance(points[0], list) or isinstance(points[0], tuple)) or len(points)<3):
		return circle(1)
	if(len(points)==1 and (isinstance(points[0], list) or isinstance(points[0], tuple))):
		points = points[0]
	vectors = []
	for point in points:
		if isinstance(point, list) or isinstance(point, tuple) :
			vectors.append(FreeCAD.Vector(point[0] if len(point)>0 else 0.0, point[1] if len(point)>1 else 0.0, point[2] if len(point)>2 else 0.0))
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "bezier_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createBezier(node, vectors,center,closed):
		node.obj = Draft.makeBezCurve(vectors,closed,support=None)
		node.obj.Label = node.name
		node.centerx = 0.0
		node.centery = 0.0
	node.addAction(createBezier, (node, vectors,center,closed))
	return node

def helix(r=1.0,p=1.0,h=1.0,center=None,d=0.0,name=None):
	r = abs(r)
	p = abs(p)
	h = abs(h)
	d = abs(d)
	if( r == 0.0 and d != 0.0):
		r = d/2.0
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "helix_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createHelix(node, r,p,h,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", node.name)
		node.obj.Shape = Part.makeHelix (p, h, r)
		node.centerx = -float(r)
		node.centery = -float(r)
		useCenter(node, center)
	node.addAction(createHelix, (node, r,p,h,center))
	return node
	
def line(p1=[0.0,0.0,0.0],p2=[1.0,1.0,1.0],center=None,name=None):
	if(not isinstance(p1,list) and not isinstance(p1,tuple)):
		p1 = [0.0,0.0,0.0]
	if(not isinstance(p2,list) and not isinstance(p2,tuple)):
		p2 = [1.0,1.0,1.0]
	p1 = ( float(p1[0]) if len(p1)>0 else 0.0, float(p1[1]) if len(p1)>1 else 0.0, float(p1[2]) if len(p1)>2 else 0.0 )
	p2 = ( float(p2[0]) if len(p2)>0 else 0.0, float(p2[1]) if len(p2)>1 else 0.0, float(p2[2]) if len(p2)>2 else 0.0 )
	global _idx_EasyNode
	node = EasyNode()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "3Dpolygon_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createLine(node, p1,p2,center):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Feature", "line_"+str(_idx_EasyNode))
		node.obj.Shape = Part.makeLine (p1,p2)
		node.centerx = p1[0] # TODO: maybe pushit to the real center of the line instead of the start?
		node.centery = p1[1]
		node.centerz = p1[2]
		useCenter(node, center)
	node.addAction(createLine, (node, p1,p2,center))
	return node
	
def text(text="Hello", size=1.0, font="arial.ttf",center=None,name=None):
	global _idx_EasyNode
	node = EasyNode2D()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "text_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createText(node, text,size,font,center):
		node.obj = Draft.makeShapeString(String=text,FontFile=font,Size=size,Tracking=0)
		node.obj.Label = node.name
		# temp_poly = Draft.makeShapeString(String=text,FontFile=font,Size=size,Tracking=0)
		# node.obj.Shape = temp_poly
		node.centerx = 0.0
		node.centery = 0.0
		useCenter(node, center)
	node.addAction(createText, (node, text,size,font,center))
	return node

def gear(nb=6, mod=2.5, angle=20.0, external=True, high_precision=False,name=None):
	global _idx_EasyNode
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "gear_"+str(_idx_EasyNode)
	else:
		node.name = name
	nb = int(nb)
	def createGear(node, nb,mod,angle,center,high_precision,external):
		gear = InvoluteGearFeature.makeInvoluteGear(node.name)
		gear.NumberOfTeeth = nb
		gear.Modules = str(mod)+' mm'
		gear.HighPrecision = high_precision
		gear.ExternalGear = external
		gear.PressureAngle = angle
		node = EasyNode2D()
		node.obj = gear
		node.centerx = 0.0 #TODO
		node.centery = 0.0
	node.addAction(createGear, (node, nb,mod,angle,center,high_precision,external))
	return node;

######### Extrusion (2D to 3D) #########

#todo: like cut, unionize auto
class EasyNodeLinear(EasyNodeColored):
	def __init__(self):
		self.edges = [];
		self.childs = []
		self.actions = []
		self.actions_after = []
		self.simple = True
	def layout_childs(self, *tupleOfNodes):
		if(len(tupleOfNodes)>=1):
			print("extrude "+tupleOfNodes[0].name)
			self.obj.Base = tupleOfNodes[0].obj
			self.obj.Base.ViewObject.Visibility = False
		return self

def z_extrude(length=1.0, angle=0.0,name=None):
	print(str(length)+" -> "+str(angle))
	global _idx_EasyNode
	node = EasyNodeLinear()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "zextrude_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createZExtrude(node, length,angle):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Extrusion", node.name)
		node.obj.DirMode = "Normal"
		node.obj.TaperAngle = angle*180.0/math.pi
		node.obj.LengthFwd = length
		node.obj.Solid = True
	node.addAction(createZExtrude, (node, length,angle))
	return node

def linear_extrude(x=0.0,y=0.0,z=0.0, angle=0.0,name=None):
	(x,y,z) = getTuple3Abs(x,y,z,0.0)
	normal = Base.Vector(x,y,z);
	length = normal.Length
	global _idx_EasyNode
	node = EasyNodeLinear()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "extrude_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createExtrude(node, x,y,z,angle):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Extrusion", node.name)
		node.obj.DirMode = "Custom"
		node.obj.LengthFwd = length
		node.obj.TaperAngle = angle
		node.obj.Dir = normal
		node.obj.Solid = True
	node.addAction(createExtrude, (node, x,y,z,angle))
	return node
	
#todo: like cut, unionize auto
class EasyNodeRotateExtrude(EasyNodeColored):
	# def __init__(self):
		# self.childs = []
		# self.actions = []
		# self.actions_after = []
		# self.simple = True
	def layout_childs(self, *tupleOfNodes):
		if(len(tupleOfNodes)>=1):
			self.obj.Source = tupleOfNodes[0].obj
			self.obj.Source.ViewObject.Visibility = False
		return self

def rotate_extrude(angle=360.0,name=None):
	angle = min(abs(angle),360.0)
	global _idx_EasyNode
	node = EasyNodeRotateExtrude()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "revolution_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createRExtrude(node, angle):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Revolution", node.name)
		node.obj.Axis = Base.Vector(0.0,1.0,0.0)
		node.obj.Base = Base.Vector(0.0,0.0,0.0)
		node.obj.Angle = float(angle)
		node.obj.Solid = True
		node.obj.AxisLink = None
		node.obj.Symmetric = False
		node.rotate(90,0,0)
	node.addAction(createRExtrude, (node, angle))
	return node

#todo: like cut, unionize auto
class EasyNodeSweep(EasyNode):
	def layout_childs(self, *tupleOfNodes):
		base = None
		tool = None
		if len(tupleOfNodes) == 2 :
			base = tupleOfNodes[0]
			tool = tupleOfNodes[1]
		elif len(tupleOfNodes) > 2 :
			base = tupleOfNodes[0]
			tool = tupleOfNodes[1]
		else:
			print("Error, wrong number of sweep elements : "+str(len(tupleOfNodes)) +" and we need 2")
			return self
		self.childs.append(base)
		self.childs.append(tool)
		self.obj.Sections = [tool.obj]
		arrayEdge = []
		i=1
		for edge in base.obj.Shape.Edges:
			arrayEdge.append("Edge"+str(i))
			i += 1
		self.obj.Spine = (base.obj,arrayEdge)
		base.obj.ViewObject.Visibility = False
		tool.obj.ViewObject.Visibility = False
		return self

#transition in ["Right corner", "Round corner","Transformed" ]
def path_extrude(frenet=True, transition = "Right corner",name=None):
	global _idx_EasyNode
	node = EasyNodeSweep()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "sweep_"+str(_idx_EasyNode)
	else:
		node.name = name
	def createPExtrude(node, frenet,transition):
		node.obj = FreeCAD.ActiveDocument.addObject("Part::Sweep", node.name)
		node.obj.Solid = True
		node.obj.Frenet = frenet
		node.obj.Transition = transition
	node.addAction(createPExtrude, (node, frenet,transition))
	return node

######### convenience objects for chaining ########
	
center = EasyNode.center
center_x = EasyNode.x
center_y = EasyNode.y
center_z = EasyNode.z
center_xy = EasyNode.xy
center_xz = EasyNode.xz
center_yz = EasyNode.yz
center_xyz = EasyNode.xyz

class ApplyNodeFunc():
	def __init__(self, func, args):
		self.args = args
		self.func = func
		self.before = []
	def __call__(self, *nodes):
		print(nodes[0])
		goodnodes = []
		if len(self.before)>0:
			goodnodes.append(self.before.pop()(*nodes))
			while len(self.before)>0:
				goodnodes[0] = self.before.pop()(goodnodes[0])
		else:
			for node in nodes:
				if(isinstance(node, EasyNode)):
					goodnodes.append(node)
		if(len(goodnodes)==0):
			print("Error, use a fucntion on no node ")
			return self
		elif(len(goodnodes)==1):
			print("do(1) "+self.func.__name__)
			if(len(self.args)==2):
				self.func(goodnodes[0],self.args[0],self.args[1])
			elif(len(self.args)==3):
				self.func(goodnodes[0],self.args[0],self.args[1],self.args[2])
			elif(len(self.args)==4):
				self.func(goodnodes[0],self.args[0],self.args[1],self.args[2],self.args[3])
			return goodnodes[0]
		else:
			print("do(union) "+self.func.__name__)
			union_obj = union(goodnodes)
			if(len(self.args)==2):
				self.func(union_obj,self.args[0],self.args[1])
			elif(len(self.args)==3):
				self.func(union_obj,self.args[0],self.args[1],self.args[2])
			elif(len(self.args)==4):
				self.func(union_obj,self.args[0],self.args[1],self.args[2],self.args[3])
			return union_obj
	#also redefine every fucntion to do the same,
	# it avoid the user to type '(' and ')' and replace it with '.'
	def translate(self, x=0.0,y=0.0,z=0.0):
		self.before.append(ApplyNodeFunc(EasyNode.move, (x,y,z)))
		return self
	def move(self, x=0.0,y=0.0,z=0.0):
		self.before.append(ApplyNodeFunc(EasyNode.move, (x,y,z)))
		return self
	def rotate(self, x=0.0,y=0.0,z=0.0):
		self.before.append(ApplyNodeFunc(EasyNode.rotate, (x,y,z)))
		return self
	def rotate2D(self, x=0.0,y=0.0):
		self.before.append(ApplyNodeFunc(EasyNode2D.rotate2D, (x,y)))
		return self
	def scale(self, x=0.0,y=0.0,z=0.0):
		self.before.append(ApplyNodeFunc(EasyNode.scale, (x,y,z)))
		return self
	def color(self, r=0.0,v=0.0,b=0,a=0.0):
		self.before.append(ApplyNodeFunc(magic_color, (r,v,b,a)))
		return self
	def union(self,name=None):
		return self(union(name))
	def inter(self,name=None):
		return self(inter(name))
	def cut(self,name=None):
		return self(cut(name))
	def chamfer(self,name=None):
		return self(chamfer(name))
	def fillet(self,name=None):
		return self(fillet(name))
	def mirror(x=0.0,y=0.0,z=0.0,name=None):
		return self(mirror(x,y,z,name))
	def offset(self,length=0.0,fillet=True,fusion=True,name=None):
		return self(offset(length=length,fillet=fillet,fusion=fusion,name=name))
	def offset2D(self,length=0.0,fillet=True,fusion=True,name):
		return self(offset2D(length=length,fillet=fillet,fusion=fusion,name=name))
	def cube(size=0.0,y=0.0,z=0.0,center=None,x=0.0, name=None):
		return self(cube(size,y,z,center,x, name))
	def box(x=1.0,y=1.0,z=1.0,center=None, name=None):
		return self(box(x,y,z,center, name))
	def tri_rect(x=1.0,y=1.0,z=1.0,center=None, name=None):
		return self(tri_rect(x,y,z,center, name))
	def cylinder(r=0.0,h=1.0,center=None,d=0.0,r1=0.0,r2=0.0,d1=0.0,d2=0.0,angle=360.0,fn=1,name=None):
		return self(cylinder(r,h,center,d,r1,r2,d1,d2,angle,fn,name))
	def cone(r1=1.0,r2=1.0,h=1.0,center=None,d1=0.0,d2=0.0,fn=1,name=None):
		return self(cone(r1,r2,h,center,d1,d2,fn,name))
	def sphere(r=1.0,center=None,d=0.0,fn=1,name=None):
		return self(sphere(r,center,d,fn,name))
	def torus(r1=1.0, r2=0.1,center=None,d1=0.0,d2=0.0,name=None):
		return self(torus(r1, r2,center,d1,d2,name))
	def poly_ext(r=1.0, nb=3, h=1.0,center=None,d=0.0,name=None):
		return self(poly_ext(r, nb, h,center,d,name))
	def createPolyExt(node, r,nb,h,center):
		return self(createPolyExt(node, r,nb,h,center))
	def poly_int(a=1.0, nb=3, h=1.0,center=None,d=0.0,name=None):
		return self(poly_int(a, nb, h,center,d,name))
# def rotate2D(self, x=0.0,y=0.0):
	def circle(r=1.0,center=None,d=0.0,fn=1,name=None):
		return self(circle(r,center,d,fn,name))
	def ellipse(r1=0.0,r2=0.0,center=None,d1=0.0,d2=0.0,name=None):
		return self(ellipse(r1,r2,center,d1,d2,name))
	def poly_reg(r=1.0,nb=3,center=None,inscr=True,d=0.0,name=None):
		return self(poly_reg(r,nb,center,inscr,d,name))
	def square(size=1.0,y=0.0,x=0.0,center=None,name=None):
		return self(square(size,y,x,center,name))
	def rectangle(x=1.0,y=1.0,center=None,name=None):
		return self(rectangle(x,y,center,name))
	def polygon(points=[], closed=True,name=None):
		return self(polygon(points, closed,name))
	def bspline(points=[], closed=False,name=None):
		return self(bspline(points, closed,name))
	def bezier(points=[], closed=False,name=None):
		return self(bezier(points, closed,name))
	def helix(r=1.0,p=1.0,h=1.0,center=None,d=0.0,name=None):
		return self(helix(r,p,h,center,d,name))
	def gear(nb=6, mod=2.5, angle=20.0, external=True, high_precision=False,name=None):
		return self(gear(nb, mod, angle, external, high_precision,name))
	def line(p1=[0.0,0.0,0.0],p2=[1.0,1.0,1.0],center=None,name=None):
		return self(line(p1,p2,center,name))
	def text(text="Hello", size=1.0, font="arial.ttf",center=None,name=None):
		return self(text(text, size, font,center,name))
	def z_extrude(length=1.0, angle=0.0):
		return self(z_extrude(length, angle))
	def linear_extrude(x=0.0,y=0.0,z=0.0, angle=0.0,name=None):
		return self(linear_extrude(x,y,z, angle,name))
	def rotate_extrude(angle=360.0,name=None):
		return self(rotate_extrude(angle,name))
	def path_extrude(frenet=True, transition = "Right corner",name=None):
		return self(path_extrude(frenet,transition,name))
	
def translate(x=0.0,y=0.0,z=0.0):
	return ApplyNodeFunc(EasyNode.move, (x,y,z))

def move(x=0.0,y=0.0,z=0.0):
	return ApplyNodeFunc(EasyNode.move, (x,y,z))

def rotate(x=0.0,y=0.0,z=0.0):
	return ApplyNodeFunc(EasyNode.rotate, (x,y,z))

def scale(x=0.0,y=0.0,z=0.0):
	return ApplyNodeFunc(EasyNode.scale, (x,y,z))
	
def color(r=0.0,v=0.0,b=0,a=0.0):
	return ApplyNodeFunc(magic_color, (r,v,b,a))
######### import & export #########

def importSvg(filename="./None.svg",ids=[],name=None):
	global _idx_EasyNode
	node = EasyNode()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "svg_"+str(_idx_EasyNode)
	else:
		node.name = name
	node.simple= False
	def importSvg_action(filename,ids=[]):
		objects_before = FreeCAD.ActiveDocument.Objects
		importSVG.insert(filename,FreeCAD.ActiveDocument.Name)
		objects_inserted = FreeCAD.ActiveDocument.Objects
		for obj in objects_before:
			objects_inserted.remove(obj)
		if(len(ids)==0):
			if(len(objects_inserted)==1):
				node.obj = objects_inserted[0]
			else:
				node.obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "union_"+str(_idx_EasyNode))
				for obj in objects_inserted:
					node(easyNodeStub(obj,"svg"))
		else:
			to_unionise = []
			for idx in ids:
				if(idx<len(objects_inserted)):
					to_unionise.append(objects_inserted[idx])
			if(len(to_unionise)==1):
				node.obj = to_unionise[0]
			else:
				node.obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "union_"+str(_idx_EasyNode))
				for obj in to_unionise:
					node(easyNodeStub(obj,"svg"))
				
	node.addAction(importSvg_action, (filename,ids))
	return node	
	
def easyNodeStub(obj, name):
	global _idx_EasyNode
	node = EasyNode()
	_idx_EasyNode += 1
	node.name = name+"_"+str(_idx_EasyNode)
	node.obj = obj
	return node

def importStl(filename=";/None.stl",ids=[],name=None):
	global _idx_EasyNode
	node = EasyNode()
	_idx_EasyNode += 1
	if(name == None or not isinstance(name, str)):
		node.name = "stl_"+str(_idx_EasyNode)
	else:
		node.name = name
	node.simple= False
	def importStl_action(filename,ids=[]):
		objects_before = FreeCAD.ActiveDocument.Objects
		Mesh.insert(filename,FreeCAD.ActiveDocument.Name)
		objects_inserted = FreeCAD.ActiveDocument.Objects
		for obj in objects_before:
			objects_inserted.remove(obj)
		if(len(ids)==0):
			if(len(objects_inserted)==1):
				node.obj = objects_inserted[0]
			else:
				node.obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "union_"+str(_idx_EasyNode))
				for obj in objects_inserted:
					node(easyNodeStub(obj,"stl"))
		else:
			to_unionise = []
			for idx in ids:
				if(idx<len(objects_inserted)):
					to_unionise.append(objects_inserted[idx])
			if(len(to_unionise)==1):
				node.obj = to_unionise[0]
			else:
				node.obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "union_"+str(_idx_EasyNode))
				for obj in to_unionise:
					node(easyNodeStub(obj,"stl"))
	node.addAction(importStl_action, (filename,ids))
	return node	
