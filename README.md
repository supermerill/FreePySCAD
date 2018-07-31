

# PySCAD
You like OpenSCAD but you hate it at the same time?
You don't like wasting your time moving the mouse?
Pyscad is for you!
## How it work
Pyscad is a python library that use FreeCAD to let user write their code in a text editor and see the result after a compilation process, like OpenSCAD but in FreeCAD.  
To install the library, clone the github repository into the "Freecad X.xx/mod" directory  
To write your code, you can open the freecad macro editor and begining your macro with "from Pyscad.pyscad import *"   
You can also type in the python console "execfile('path_to/my_pycad.py')", this has the advantage to show the errors.
## what's different
The braces are replaced with parenthesis  
The ';' are replaced with ',' and you also have to place it after ')' if no other ')' are directly after that to respect the python syntax.  
You can't let the modifiers like translate, rotate... be unattached: use the parenthesis or a dot (see below)

    openscad: difference(){ translate([1,1,0]) cube(2); rotate([0,0,45]) cube(2); }
    pyscad:   difference()( translate([1,1,0]).cube(2), rotate([0,0,45])(cube(2)),)
minkowski and hull aren't coded.  
minkowski can be replaced by offset() for the most simple case (sphere)

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
* helix(r,p,h,center) # p = pitch = height between the begin and the end of a loop

#### 1D&2D:
* circle( r)  
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


#### 2D to 3D:
* linear_extrude(height,convexity,twist,slices,scale)  
* rotate_extrude(angle)  
* path_extrude(frenet,transition)(path1D, patron2D)  

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

#### Modifiers:
* .x/y/z() / .center()
* translate/move(x,y,z)(...3D) / move([x,y,z])(...3D) / .move(x,y,z) / .move([x,y,z]) / move(x,y,z).somethingelse  
* rotate(x,y,z)(...3D) / rotate([x,y,z])(...3D) / .rotate(x,y,z) / .rotate([x,y,z]) / rotate(x,y,z).somethingelse  
* scale(x,y,z)(...3D) / scale([x,y,z])(...3D) / .scale(x,y,z) / .scale([x,y,z]) / scale(x,y,z).somethingelse  
* .color("colorname") / color(r,g,b,a) / color([r,g,b,a]) / color(something)(...) / color(something).somethingelse  
* .multmatrix(m)  

#### Transformations:
* mirror(x,y,z)(...) / mirror([x,y,z])(...)  
* chamfer().setAngle(radius,edge_id...)(...3D) # edge_id can be show my moving the mouse on the edge in the gui  
* fillet().setAngle(radius,edge_id...)(...3D)  
* offset(length,fillet,fusion)(...3D)  
* offset2D(length,fillet,fusion)(...2D)  

#### 3D Boolean operations:
* union()(...3D) / union().add(...3D)  
* inter()(...3D)  
* cut()(...3D) / difference()(...3D)  

#### Other:
* scene().draw(...3D) / scene().redraw(...3D) #redraw() erase everything in the document before rebuilding the object tree. Draw() try to update when possible and don't erase everything.
* importSvg(filepath,ids) #ids is an optional array of index to say which one have to be imported
* importStl(filepath,ids) 

All python language and standard library

### notes: 
* ...3D represent a list (possibly empty) of 3D node
* you can replace )(...) by ).add(...) for union, difference and
* center: on almost every object, you can set as parameter, center=True or center=center_x, center=center_yz, ...
	you can also use the transformation .center() or .x(), .yz(), ....
* name: on almost everything, you can set the name parameter to whatever you want, it will be shown in the FreeCAD object hierarchy.
* the notation move(2).box(1) should be used only whne it's very convenient, It's here to make conversion from openscad to pyscad more easy, but It can led to strange behavior, see the two points below.
* Order of execution: move(6)(move(3).move(2).cube(1).move(4).move(5)) => it's ugly, don't do that.
* the move(2).box(1) work but you cannot do move(1).myfunc() because myfunc isn't in the list of function that is available to the "move object". In this case, you have to use move(1)(myfunc()) or myfunc().move(1)
