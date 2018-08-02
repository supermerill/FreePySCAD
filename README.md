

# PySCAD
You like OpenSCAD but you hate it at the same time?
You don't like wasting your time moving the mouse?
Pyscad is for you!
## How it work
Pyscad is a python library that use FreeCAD to let user write their code in a text editor and see the result after a compilation process, like OpenSCAD but in FreeCAD.  
To install the library, clone the github repository into the "Freecad X.xx/mod" directory  
To write your code, you can open the freecad macro editor and beginning your macro with "from Pyscad.pyscad import *"   
You can also type in the python console "execfile('path_to/my_pycad.py')", this has the advantage to show the errors.
## what's different
The braces are replaced with parenthesis  
The ';' are replaced with ',' and you also have to place it after ')' if no other ')' are directly after that to respect the python syntax.  
You can't let the modifiers like translate, rotate... be unattached: use the parenthesis or a dot (see below)

    openscad: difference(){ translate([1,1,0]) cube(2); rotate([0,0,45]) cube(2); }  
    pyscad:   difference()( translate([1,1,0]).cube(2), rotate([0,0,45])(cube(2)),)  
resize, minkowski and hull aren't implemented.  

You can also wrote a more concise code with Pyscad if you want (i was tired of writing "translate([ ])" over an over)

    cut()( move(1,1).cube(2), cube(2).rotate(0,0,60) , rotate(z=30)(cube(2)) )

You can now use functions with real variables that can be changed!

	from Pyscad.pyscad import *
	def make_T(l,h):
		big = box(l,w,h)
		l = l/3.0
		h = 2.0*h/3.0
		return cut("T")(
			big,
			box(l,w,h),
			box(l,w,h).move(l*2),
		)
    w=10
	T_10cube = make_T(10,10)
	w=3
	T_3cube = make_T(10,10)
	scene().show(
		T_10cube,
		T_3cube.move(12),
	)
You also have to pass your objects inside the scene.show() function to put it into the FreeCAD environment.
This function do the work of recreating only the node that need a redraw and don't touch the objects you may have added manually into FreeCAD. 

## pyscad cheatsheet:

#### 1D:
* line([x1,y1,z1],[x2,y2,z2],center)
* arc([x1,y1,z1],[x2,y2,z2],[x3,y3,z3],center)
* helix(r,p,h,center) # p = pitch = height between the begin and the end of a single loop

#### 1D / 2D:
* circle(r)  
* ellipse(r,l)  
* polygon([points],closed)  
* bspline([points],closed)  
* bezier([points],closed)  

#### 2D:
* square(size)  
* square([width,height]) / square(width,height) / rectangle([width,height])  
* poly_reg(r|d,nb,center,inscr)  
* text(text,size)  
* gear(nb, mod, angle, external, high_precision)  


#### transformation 1D to 2D to 3D:
* create_wire()(...1D) #create a new wire from many edges, can be extruded if they are connected
* linear_extrude(height,convexity,twist,slices,scale)(obj_2D)  
* rotate_extrude(angle)(obj_2D) #rotate over the Z axis  
* path_extrude(frenet,transition)(path_1D, patron_2D)  

#### 3D:
* sphere(r|d,fn)  
* cube(size)  
* box(x,y,z) / box([width,depth,height],center)  
* triangle(x,y,z) / triangle([width,depth,height],center)  
* cylinder(r|d,h,fn,angle)  
* cone(r1|d1,r2|d2,h,fn) cylinder(r1|d1,r2|d2,h,fn)  
* torus(r1,r2,h)  
* poly_ext(r,nb,h) # r = radius, nb = nb vertex (min 3)  
* poly_int(a,nb,h) # a = apothem, nb = nb vertex (min 3)  
* polyhedron(points, faces) # for debugging use polyhedron_wip : it creates a group of points & faces instead of a 3D model  

#### 3D Boolean operations:
* union()(...3D) / union().add(...3D)  
* intersection()(...3D)  
* difference()(...3D) / cut()(...3D)  

#### Transformations:
* mirror(x,y,z)(...) / mirror([x,y,z])(...)  
* chamfer().setAngle(radius,edge_id...)(...3D) # edge_id can be show my moving the mouse on the edge in the gui  
* fillet().setAngle(radius,edge_id...)(...3D)  
* offset(length,fillet,fusion)(...3D)  
* offset2D(length,fillet,fusion)(...2D)  

#### Modifiers:
* .x/y/z() / .center()
* translate/move(x,y,z)(...) / move([x,y,z])(...) / .move(x,y,z) / .move([x,y,z]) / move(x,y,z).stdfuncXXX(  
* rotate(x,y,z)(...) / rotate([x,y,z])(...) / .rotate(x,y,z) / .rotate([x,y,z]) / rotate(x,y,z).stdfuncXXX(  
* scale(x,y,z)(...) / scale([x,y,z])(...) / .scale(x,y,z) / .scale([x,y,z]) / scale(x,y,z).stdfuncXXX(  
* .color("colorname") / color(r,g,b,a) / color([r,g,b,a]) / color(something)(...) / color(something).stdfuncXXX(  
* .multmatrix(m)  

#### Other:
* scene().draw(...3D) / scene().redraw(...3D) #redraw() erase everything in the document before rebuilding the object tree. Draw() try to update when possible and don't erase everything.
* importSvg(filepath,ids) #ids is an optional array of index to say which one have to be imported
* importStl(filepath,ids) 
* group()(...) # a group of nodes (1D, 2D & 3D can be mixed), for viewing purpose only as it can't be used by anything. You can use the modifiers, though.

All python syntax and standard library can be used  

### notes: 
* ...3D represent a list (possibly empty) of 3D node
* You can replace )(...) by ).add(...) for union, difference and
* Center: on almost every object, you can set as parameter, center=True or center=center_x, center=center_yz, ...
	you can also use the transformation .center() or .x(), .yz(), ....
* Name: on almost everything, you can set the name parameter to whatever you want, it will be shown in the FreeCAD object hierarchy.
* The notation move(2).box(1) should be used only when it's very convenient, it's here mainly to make conversion from openscad to pyscad more easy, but it can led to strange behaviors, see the two points below.
* Order of execution: move(6)(move(3).move(2).cube(1).move(4).move(5)) => it begin at the object then move away from it. 
* The move(2).box(1) work but you cannot do move(1).myfunc() because myfunc isn't in the list of functions that is available to the "move object". In this case, you have to use move(1)(myfunc()) or myfunc().move(1)
* When a part fail to compile, it creates a sphere of size _default_size. you can change the variable _default_size, it's used as a default value when 0.0 will create an impossible object. Example: circle() == circle(_default_size).