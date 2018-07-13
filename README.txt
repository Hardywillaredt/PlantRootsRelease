SOFTWARE SETUP

Requirements...

Python 3.5		
PYQT5 (directions for installation of pyqt5 found here... http://pyqt.sourceforge.net/Docs/PyQt5/installation.html)



Running the software

Once python is set up with pyqt5, you may launch the program by navigating to this directory within your python environment, and calling the command

python UI_Manager.py


Assuming that PYQT5 is properly installed, and all of the files in this repo are present, the program should launch.


Use

Loading and saving root skeletons, as well as loading mesh files can be managed from the File menu on the top left.  The remaining options in the toolbar menus are currently either deprecated or disabled.

Once loaded, the panels flanking the screen can be used to respectively alter viewing options (left), or perform editing options upon the skeleton (right)



Visualization Options

The viewing options are broken into how Nodes (junctions or endpoints of roots in the skeleton), Edges (collections of edges branching between junctions and endpoints), and the Mesh (if it is loaded) are viewed.

Nodes and Edges can be colored by their Thickness, Width, Ratio (Thickness/Width), and Connected Component (each component being one set of nodes and edges which are all interconnected), relative to the other nodes and edges in the skeleton.  Additionally, Nodes may be colored by their relative degree, or a single flat color.  To color the nodes or edges a certain manner, you must first select a parameter by which to color them, and a heatmap type from the dropdown menus.  The parameters for their relative colorings may be adjusted by using the "Color Cieling" and "Color Floor" sliders.  By adjusting the 'Floor' value up, any elements of the skeleton which fall below that relative ration along the chosen parameter will be clamped to the bottom end of the provided heatmap.  Similarly for the 'Cieling' selection.

You may also choose the size of the different kinds of Nodes (endpoints and junctions), and whether to display them.

The "Magnify Suggested Edges" and "Display Only Suggested" options well either magnify or limit all displayed edges to those which form part of a loop.  This should help determine areas where edges need to be removed or fixed up.


The Mesh can be loaded, and its color and transparency adjusted in the "Mesh Visualization" section of this window



Editing Operations

There are 3 different modes of editing operations: Connection, Edge Removal, and Edge Splitting.  In order to edit the skeleton, you will need to click the button corresponding to the desired mode, and then make selections of nodes or edges in the skeleton view corresponding to the edits you would like to make.  There is currently NO visual indicator of what the current mode (if any) is.  This should change in the near future, but if you are unsure what mode you are in, you may simply click the button for the mode you desire.

Connection Mode-

	While in connection mode, you may select nodes in the skeleton/graph view by clicking on them.  You may only select nodes which belong to different connected components.  If the existing endpoints or junctions that exist in the graph visualization do not correspond to where you would like to make a connection (eg. there is a connection missing at the branching point of a root), you may select any of the underlying vertices on the skeleton by clicking near them.  Once one node is selected each upon two separate components, you may click the "Accept Connection" button to create a new edge between those nodes.

	Also while in connection mode, you may select components from the drop-down menus in the same panel (the components are sorted by the total length of their connected edges, largest components first) and restrict the items displayed to only those components, which may help you more easily identify where likely connections should be.

	Finally, you can display the bounding boxes for the different components in the skeleton through the corresponding checkbox.  This again can serve as a visual cue to help narrow in on missing connections

Edge Removal and Splitting information -
	
	There is a textbox in the removal panel entitled "Number of Edges Required to Disconnect" - this number will indicate the total number of edges that need to be removed from the skeleton in order to remove all loops.

Edge Removal Mode -
	
	While in edge removal mode, if you click on an edge in the skeleton, it should become highlighted in white, and scaled up.  If the selected edge is one that you would like to remove, you may then click the "Accept Removal" button, and it will be deleted from the graph.  This can be used to remove errant connections between nodes, abandoned edges etc.

Edge Splitting Mode -
	
	The edge splitting mode is primarily intended for situations where two branches come closely together and then split appart eg...

    |    |
     \  /
      \/
      |
      |
      /\
     /  \
    |    |


    and can be used to split the merged middle edge so that you have two separate parallel roots - eg...

    |    |
     \  /
     /  \
     |  |
     |  |
     \  /
     /  \
    |    |

   	To accomplish this, while in the edge splitting mode, you will first select the center edge that you would like to split (which will highlight it in white), and then select the two or more edges coming out of that central edge that correspond to a single root.  Eg. in the above scenario, you might first click the center edge, and then the edge on the top right, and then the edge on the bottom right.  Once the set of edges that go together to form a single root are selected, you can click the "Accept Removal" operation to perform the operation.