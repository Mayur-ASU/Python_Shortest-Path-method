# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 16:05:47 2021
@author: Mayur Patil, Arizona State University

This module is developed for transportation network modeling.
It includes the following four classes:
    Node
    Link
    OD
    Network
"""

import sys
import traceback
import utils

class Node:
   """
   This class describes Node object as for a transportation network.
    
   Each node has the following attributes:
      ID (int), isZone (boolean)
      forward star (list of Links), reverse star (list of Links)
      
      potential (float): used for shortest path finding
      pre (Node): preceding node, used for shortest path finding
   
   In keeping with the TNTP format, the zones/centroids are assumed to have 
      the lowest node IDs (1, 2, ..., numZones).
   """
   def __init__(self, id, isZone = False):
      self.ID = id
      self.isZone = isZone
      self.forwardStar = []
      self.reverseStar = []
      
      self.potential = float('inf')
      self.pre = None
      
   def __str__(self):
      info = ("node " + str(self.ID) + ": out degree = " + 
            str(len(self.forwardStar)) + ", in degree = " +
            str(len(self.reverseStar)))
      return info
   
   def __repr__(self): 
      return ("node " + str(self.ID))
   
   def ResetPotential(self):
      self.potential = float('inf')
      self.pre = None
   
class OD:
   """
   This class describes OD object in a network.
   
   Each instance of the OD object has the following attributes:
      origin (int), destination (int), demand (float)
      shortestPath (list of int, as sequence of nodes)
   """
   def __init__(self, origin, destination, demand):
      self.origin = origin
      self.destination = destination
      self.demand = demand
      self.shortestPath = None
   
   def __str__(self):
      info = ("OD(" + str(self.origin) + ", " + str(self.destination)
              + "): demand = " + str(self.demand))
      return info

   def __repr__(self):
      return str(self.demand)      
    
class Link:
   """
   This class describes link object in a network.
    
   Each link instance has the following attributes:
      tail (int), head (int); 
      ID (int): order as the links are created
      
      capacity (float), length (float), freeFlowTime (float),
      alpha (float), beta (float), speedLimit (int),
      toll (float), linkType ();
      
      flow (float), cost (float): generalized travel cost 
    
   Each link instance has the following methods:
      CalcCost(): calculates generalized link travel cost as weighted sum of 
         link travel time, link travel distance, and toll rate. 
   """
   def __init__(self, tail, head, ID, capacity = 99999, length = 99999, 
      freeFlowTime = 99999, alpha = 0.15, beta = 4, 
      speedLimit = 99999, toll = 0, linkType = 0):
      self.tail = tail
      self.head = head
      self.ID = ID
      self.capacity = capacity
      self.length = length
      self.freeFlowTime = freeFlowTime
      self.alpha = alpha
      self.beta = beta
      self.speedLimit = speedLimit
      self.toll = toll
      self.linkType = linkType
      self.flow = 0
      self.cost = None
   
   def __str__(self):
      info = ("link (" + str(self.tail) + ", " + str(self.head) + "): "
              + "cost = " + str(self.cost) + ", flow = " + str(self.flow))
      return info                 

   def __repr__(self):
      info = ("link (" + str(self.tail) + ", " + str(self.head) + ")")
      return info    

   def CalcCost(self, distanceFactor = 0, tollFactor = 0):
      """
      This is a method of the Link class. 
      It calculates the generalized link cost for a Link object, and updates
         its cost attribute.  The function does not return anyvalue.
      The genealized travel time is calculated as weighted sum of the travel 
         time, travel distance, and toll rate on the link.  Link travel 
         time follows BPR function with parameters:capcity, freeFlowTime, 
         alpha, and beta
      """
      #  *** YOUR CODE HERE ***
      # Cost = Travel_time + Distance_Cost + Toll_cost
      
      travelT = self.freeFlowTime*(1+self.alpha*(self.flow/self.capacity)**self.beta)
      DistanceCost = distanceFactor*self.length
      TollCost = tollFactor*self.toll
      self.cost = travelT+DistanceCost+TollCost
      
      #self.cost = self.freeFlowTime*(1+self.alpha*(self.flow/self.capacity)**self.beta) + distanceFactor*self.length + tollFactor*self.toll
      
      
      # Replace the following with your code. 
    #  print("\n\nThe CalcCost function is not implemented.",
            #"  Write your own code to calculate the link cost function.\n\n")
      # raise utils.NotYetAttemptedException

    
class Network:
   """
   This class describes the Network object.
    
   Each network instance has the following attributes:
      
      numZones (int);  
      numNodes (int); 
      nodes (list of Node objects);
      firstThroughNode (int): in the TNTP data format, 
         transiting through nodes with low IDs can be prohibited 
         (typically for centroids). Those nodes should not be used when 
         implementing shortest path or other routefinding algorithms, 
         unless it is the destination;
      
      numLinks (int); 
      links (dictionary of Link objects): the keys are tuples 
         of integers (tail, head); links[(i,j)] is a Link object        
      tollFactor (float); 
      distanceFactor (float);
      
      totalDemand (float)      
      ODpairs (dictionary of dictionarys of OD objects): 
         two-level dictionarys with integers keys;
         ODpairs[i][j] is an OD object with orig i and dest j           
      
   Each network instance has the following methods:
      ReadNetworkFile(networkFileName)
      ReadDemandFile(demandFileName)
      ShortestPath(origin): shortest paths from origin to all nodes
      AON (all or nothing assignment)
      UE (static user equilibrium assignment)   
   """

   # Initialize an object of class Networks
   def __init__(self, networkFileName = None, demandFileName = None):
      """     
      This is the initialization function of the Network class. 
      An empty placeholder network will be created if neither the network 
         nor the demand files are provided.
      The function calls the ReadNetworkFile and ReadDemandFile methods of 
         the Network class to populate attributes of a Network object.      
      """
      # Create placeholders
      self.numZones = None      
      self.numNodes = None
      self.nodes = []        
      self.firstThroughNode = 0
      
      self.numLinks = None
      self.links = {}
      self.tollFactor = None
      self.distanceFactor = None
      
      self.totalDemand = 0
      self.ODpairs = {}
            
      # Read in data from files
      if networkFileName is None:
         print("\nNo network file provided.",
                "  An empty placeholder Network object is created.")
      elif demandFileName is None:
         print("\nNo demand file provided.", "  A Network object is created",
               " with topological information only.")
      else:   
         self.ReadNetworkFile(networkFileName)
         self.ReadDemandFile(demandFileName)
  
   # Read in data from network file
   def ReadNetworkFile(self, networkFileName):
      """
      This function reads network topology data from the TNTP data format, and 
         poputlates the relevant attributes of a Network object. In keeping 
         with this format, the zones/centroids are assumed to have the lowest 
         node IDs (1, 2, ..., numZones).
      It performes validity checks regarding the number of nodes, links, and 
         zones, using metadata provided in the TNTP data file.
      """   
      try: # try opening network file given as networkFileName
         networkFile = open(networkFileName, "r")
      except IOError:
         print("\nError reading network file %s" % networkFileName)
         traceback.print_exc(file=sys.stdout) 
         print("\nError reading network file %s" % networkFileName)
         traceback.print_exc(file=sys.stdout)     
 
      # Read in lines in the file as a list of strings
      fileLines = networkFile.read().splitlines() 
      
      # Read in metadata from the network file as a dictionary
      metadata = utils.readMetadata(fileLines)      
      try: # try reading all expected metadata
         self.numNodes = int(metadata['NUMBER OF NODES'])
         self.nodes = [None]*self.numNodes
         self.numLinks = int(metadata['NUMBER OF LINKS'])
         self.firstThroughNode = int(metadata['FIRST THRU NODE'])
         if self.numZones != None:
            if self.numZones != int(metadata['NUMBER OF ZONES']):
               print("\nError: Number of zones in network and demand files", 
                     "do not match.")
               raise utils.BadFileFormatException
         else:
            self.numZones = int(metadata['NUMBER OF ZONES'])                                      
      except KeyError: # KeyError
         print("\nWarning: Not all metadata present, ",
               "error checking will be limited and code will ",
               "proceed as though all nodes are through nodes.")
            
      # Add toll and distance factors      
      self.tollFactor = float(metadata.setdefault('TOLL FACTOR', 0))
      self.distanceFactor = float(metadata.setdefault('DISTANCE FACTOR', 0))
            
      # Read in links line by line and construct the network
      linkID = 0              
      for line in fileLines[metadata['END OF METADATA']:]:
               
         # Ignore comments and blank lines
         line = line.strip()
         commentPos = line.find("~")
         if commentPos >= 0: # strip comments
            line = line[:commentPos]               
         if len(line) == 0: # blank line
            continue                 
               
         # Read in link data   
         data = line.split() 
               
         # Handle link data not properly formatted
         if len(data) < 11 or data[10] != ';' :
            print("\nLink data line not formatted properly:\n '%s'" % line)
            raise utils.BadFileFormatException
                  
         # Create link
         tail = int(data[0]) 
         head = int(data[1])                
         tempLink = Link(tail, head,  
            linkID + 1,       # ID, as natural integers      
            float(data[2]),   # capacity
            float(data[3]),   # length
            float(data[4]),   # free-flow time 
            float(data[5]),   # BPR alpha
            float(data[6]),   # BPR beta
            float(data[7]),   # Speed limit
            float(data[8]),   # Toll
            data[9])          # Link type         
         # Check if data is valid for this link
         if tempLink.capacity < 0 or tempLink.length < 0 or \
            tempLink.freeFlowTime < 0 or tempLink.alpha < 0 or \
            tempLink.beta < 0 or tempLink.speedLimit < 0 or \
            tempLink.toll < 0:                    
            print("\nLink (" + data[0] + ", " + data[1] + ")",  
                  "has negative parameters.")
            raise utils.BadFileFormatException
         # Calcualte link travle cost
         tempLink.CalcCost(self.distanceFactor, self.tollFactor)
         # Add link to the dictionary         
         self.links[(tail,head)] = tempLink        
         #print("Link (" + data[0] + ", " + data[1] + ") created.")
                     
         # Create nodes if necessary,
         # then update their forward and reverse stars accordingly
         for i in range(2): # check both end nodes of the current link            
            nodeID = int(data[i]) - 1
            if nodeID >= self.numNodes:
               print("\n   Warnining: The number of nodes given in ",
                  "the metadata is ", self.numNodes, ".",
                  " Node ID", data[i], " exceeds this value.")
            if self.nodes[nodeID] is None: # create tail node                  
               self.nodes[nodeID] = Node(nodeID + 1,
                  True if nodeID + 1 <= self.numZones else False)
            #print("   Node " + data[0] + " created.")
            if i == 0: # tail node, update forwardStar   
               self.nodes[nodeID].forwardStar.append(tempLink)                  
            else: # head node, update reverseStar
               self.nodes[nodeID].reverseStar.append(tempLink) 

         # Move to next line in metadata (next link)
         linkID = linkID + 1
            
      # Network data loaded.  Perform verifications
      valid = True      
      # verify that the number of entries in the list of links 
      # matches the numLinks field
      if self.numLinks != linkID:
         print("Warning: the number of links created does not match", 
               "the number of links given in the metadata.")
         self.numLinks = linkID
         valid = False                      
      # Verify that the list of nodes does not have empty entries
      for node in self.nodes:
         if node is None:
            print("Warning: the number of nodes in the metadata ", 
                  "is greater than the number of nodes created.")
            valid = False           
      # Verify that the number of zones matches the value given in metadata
      numZones = len([i for i in self.nodes if i.isZone == True])
      if numZones != self.numZones:
         print("Warning: Number of zones given in network file ",
               "is different from the value in metadata")
         valid = False
         self.numZones = numZones
      # Print Receipt         
      if valid:         
         print("\n\nNetwork created.",
               "\nThe network passed all validity checks.")
         print("The network includes a total of " + str(self.numNodes) 
               + " nodes, " + str(self.numLinks) + " links, and " 
               + str(self.numZones) + " zones.")
      else:
         print("\n\nNetwork created.",
               "\nBut there is something wrong with the network data.")
         
   # Read in data from demand file
   def ReadDemandFile(self, demandFileName):
      """
      This function reads the demand data (OD matrix) from a demand file 
         in the TNTP format, and update a network object accordingly.
      Input parameter: demandFileName as str
      Output parameter: none
      """
      try: # try opening demand file given as demandFileName
         demandFile = open(demandFileName, "r")
      except IOError:
         print("\nError reading network file %s" % demandFileName)
         traceback.print_exc(file=sys.stdout) 
         print("\nError reading network file %s" % demandFileName)
         traceback.print_exc(file=sys.stdout)
          
      # Read in lines in the file as a list of strings
      fileLines = demandFile.read().splitlines()
            
      # Read in metadata from the demand file as a dictionary                      
      metadata = utils.readMetadata(fileLines)      
      try: # try reading all expected metadata
         totalDemand = float(metadata['TOTAL OD FLOW'])
         if self.numZones != None:
            if self.numZones != int(metadata['NUMBER OF ZONES']):
               print("Error: Number of zones in network and demand files", 
                     "do not match.")
               raise utils.BadFileFormatException
         else:
            self.numZones = int(metadata['NUMBER OF ZONES'])
      except KeyError: # KeyError
         print("Warning: Not all metadata present in demand file, ",
               "error checking will be limited.")
           
      # Initialize various variables for record keeping, 
      # and read in OD information line by line
      numOrigins = 0
      numDestinations = 0
      numODpairs = 0
      origin = None
      for line in fileLines[metadata['END OF METADATA']:]:
               
         # Ignore comments and blank lines               
         line = line.strip()               
         commentPos = line.find("~") 
         if commentPos >= 0: # strip comments
            line = line[:commentPos]
         if len(line) == 0: # blank line
            continue                              
               
         # Read in a line of OD information
         data = line.split() 
               
         # Encounter the start of a new group of OD pairs with the same origin    
         if data[0] == 'Origin':
            
            # Verify the previous group of destinations with the same origin
            if numOrigins > 0:
               if len(self.ODpairs[origin]) != numDestinations:
                  print("Warning: there is something wrong when creating",
                        " OD pairs with origin node " + str(origin)) 
                  raise utils.BadFileFormatException
                  
            # Start the new group of OD pairs with he same origin
            origin = int(data[1])
            
            # Verify the origin node is in the network, is a zone,
            # and is a new origin that has not been recorded before
            if origin > self.numNodes:
                print("Warning: the origin node " + data[1] +
                      "is not found in the network.")
                raise utils.BadFileFormatException
            elif not self.nodes[origin - 1].isZone:
               print("Warning: the origin node " + data[1] +
                     " is not designated as a zone.")
               raise utils.BadFileFormatException                                  
            elif origin in self.ODpairs:
               print("Warning: the origin node " + data[1] +
                     " shows up more than once in the demand file.")
               raise utils.BadFileFormatException                                   
            
            # Origin is valid, do the following:
            # keep track of the counter     
            numOrigins += 1                     
            # initialize the dictionary of OD objects for this origin node            
            self.ODpairs[origin] = {}
            # start the counter of destinations for this origin  
            numDestinations = 0 
            continue

         # Encounter a line with destination nodes of the same origin node
         # The number of entries in this line should be multiples of 3.
         # This is becasue each destination is given in the format of
         # "destination : demand;"
         if len(data) % 3 != 0:
            print("Demand data line not formatted properly:\n %s" % line)
            raise utils.BadFileFormatException                                  
         
         # Read in the line of destinations and create corresponding OD pairs   
         for i in range(int(len(data) // 3)): # for each destination
            
            # The first entry is the destination node itself 
            destination = int(data[i * 3])
            # verify the destination node is in the network, and is a zone 
            if destination > self.numNodes:
                print("Warning: the destination node " + str(destination) +
                      "is not found in the network.")
                raise utils.BadFileFormatException
            elif not self.nodes[destination - 1].isZone:
               print("Warning: the destination node " + str(destination) +
                     "is not designated as a zone.")
               raise utils.BadFileFormatException 
            
            # The second entry is ":"
            check = data[i * 3 + 1]
            if check != ':' : 
               print("Demand data line not formatted properly:\n %s" % line)
               raise utils.BadFileFormatException
            
            # The third entry is "demand;"
            # Remove the ";" then convert to float
            # Check the demand is positive
            demand = data[i * 3 + 2]
            demand = float(demand[:len(demand)-1])
            if demand < 0:
               print("Error: OD pair (" + str(origin) + ", " + str(destination)
                     + ")  has negative demand")
               raise utils.BadFileFormatException
            elif demand > 0: # only creates OD pair with positive demand 
               # Creat OD pair once the data passes all checks
               numDestinations += 1               
               numODpairs += 1               
               self.ODpairs[origin][destination] = \
                  OD(origin, destination, demand)
               self.totalDemand += demand
              
      # Demand data loaded.  Perform verifications.  
      valid = True
      # Verify the total demand matches that given in the metadata
      if self.totalDemand != totalDemand:
         print("Warning: the total demand does not match the value ",
               "given in the metadata.")
         valid = False            
      # Print receipt
      if valid:         
         print("\n\nNetwork demand loaded.",
               "\nThe demand information passed all validity checks.")
         print("The network includes a total of " + str(numODpairs) 
               + " OD pairs. ")
      else:
         print("\n\nNetwork demand loaded.",
               "\nBut there is something wrong when loading the data.")  
               
   def ShortestPath(self, origin):
      """
      This is a method of the Network class.
      It implements Dijkstra's algorithm to find shortest paths from 
         one origin to many destinations.
      Input parameter: origin as int
      Output parameter: tuple of tuples (node potential, preceding node) 
         for each node
      """      
      # INITIALIZATION
      # Reset potenial for all nodes
      for node in self.nodes:
         node.ResetPotential()         
      # Set the potential of the origin node to 0
      originNode = self.nodes[origin-1]
      originNode.potential = 0      
      # Set the list of the indices (not IDs) of the nodes to scan
      # as all nodes, starting from the first through node
      scanList = [i for i  in range(self.firstThroughNode - 1, self.numNodes)]     
      
      # MAIN CALCULATION
      while scanList != []:
         # Choose the node with the minimum potential from scanList
         potentials = [self.nodes[i].potential for i in scanList]
         minPotential = min(potentials)
         pos = potentials.index(minPotential)
         nodeIndex = scanList[pos]
         currentNode = self.nodes[nodeIndex]
         # Remove currentNode from scanList
         scanList.pop(pos)       
         # Update the potential of immediate downstream nodes of currentNode
         for link in currentNode.forwardStar:
            node = self.nodes[link.head-1]
            if node.potential > currentNode.potential + link.cost:  
               node.potential = currentNode.potential + link.cost
               node.pre = currentNode.ID               
         
      # OUTPUT
      # print("\n---Shortest Path Finding Results---\n")
      # for link in self.links:
      #    print(link)
      # print("\n")
      # for node in self.nodes:
      #    print(node)
      #    print("   potential = " + str(node.potential) + ", pre = " + str(node.pre))              
      return tuple((node.potential, node.pre) for node in self.nodes)

   def AON(self):
      """
      This is a method of the Network class.
      It performs all or nothing assignment for a Network object.
      Input parameter: none
      Output parameter: AON assignment results as a dictionary of floats.
         The dictionary should have the same keys as those of the links 
         attribute of a Network object (i.e., each entry represents a link).
         The value of each entry is the link flow after AON assignment.
         Note that this method does not alter the link objects 
         of the network directly.
      """
      #  *** YOUR CODE HERE ***
      # Initialize our output variable (create placeholder)
      ij = list (self.links.keys())
      #flowAON = dict(zip((ij),[0]*len(ij)))
      AON_flow = dict(zip((ij),[0]*len(ij)))
    
     # networkFileName = "SiouxFalls_net.txt"
     # demandFilename = "SiouxFalls_trips.txt"

        # tail_star = Network(networkFilename, demandFileName)
     
      #Instruction
      #1.For each OD pair in the network (self)
      #2.find Shortest path (call shortestPath method in the network),
      #3.Start from the destination, trace back until we arrive at the origin.
      #4.while we trace back, assign total demand of this OD pair
      #5.to the current link (put value into placeholder variable)

     # for O in self.ODpairs:
      #    short_pathO = self.ShortestPath(O)
       #   for D in self.ODpairs[O]:
        #      expec_demand  = self.ODpairs[O][D].demand
              
         #     c = D
          #    SP = short_pathO[c-1][1]
           #   while SP is not None:
            #      flowAON[(SP,c)] += expec_demand
             #     SP = short_pathO[c-1][1]
               
             #     c = SP
      #return flowAON
      
      for o in self.ODpairs:
          SPath = self.ShortestPath(o)
          for d in self.ODpairs[o]:
              demands = self.ODpairs[o][d].demand
              
              x = d
              while SPath[x-1][1] is not None:
                  AON_flow[(SPath[x-1][1], x)] += demands
                  
                  x = SPath[x-1][1]
      return AON_flow
      
              
      #return flowAON
      

 
      #Pseudo-code
      #For each origin O
      #for o in self.ODpairs:
          
    # 1. find shortest path to all nodes starting from the origin node O
    #    (by calling the ShortestPath method of Network self)
    # 2. for each destination node d such that (o,d) is an OD pair
    # (for d in self.ODpairs[o]:) 
    #use while loop to implement the following:
        # Start from the destination, trace back until we arrive at the origin. 
        # while we trace back, assign total demand of this OD pair.
        # To the current link (put value into the placeholder variable).  
      
        
      # Replace the following with your code.          
#      print("\n\nThe AON function is not implemented.",
#            "  Write your own code to implement the all or nothing assignment.\n\n")
#      raise utils.NotYetAttemptedException

  
   def UE(self, tolerance = 10**(-2)):
      """
      This is a method of the Network class.
      It performs UE assignment for a Network object. The Frank-Wolfe algorithm
         with method of successive average is implemented.
      Input parameter: tolerance (float)
      Output parameter: none. This method alters the link objects 
         of the network directly.
      """
      #  *** YOUR CODE HERE ***
      #Intialize the AON link flow 
      flow_AON = self.AON()
      
      #Identifying each link in the self.links
      #(tuple) assigning the corresponding value to flow_AON on each link
      
      for ij in self.links:
          self.links[ij].flow = flow_AON(ij)
     # Assigning AON link flow to each link
     
     #Initializing the convergence metric
     #Choose convergence value very large.

      converge = 5
     
     # we have to set iteration counter to 1.
      IteCou = 1
     
     #use the while loop, until the convergence metric is less than the tolerance value.
      while (converge > tolerance):
         # updating link cost on each link
         # Using calcost function used to link cost for a Link object, and update sits cost attribute. 
         for ij in self.links:
             self.links[ij].CalcCost()
             
             flow_AON = self.AON() 
             # Again calculating AON using the updated link cost.
             
             epsilon = []
             
             for ij in self.links:
                 C_flow = self.links[ij].flow
                 move = C_flow + (flow_AON[ij]-C_flow)/ IteCou
                 if move == 0:
                     E_ij = 0
                 else:
                     E_ij = abs ((C_flow-move)/move)
                     
                     
                     self.links[ij].flow = move
                     epsilon.append(E_ij)
                     print('%s' % self.links[ij])
                     print('progress of iteration: %' % counter)
                     error = max(epsilon)
                     print('Error after %s iterations is: %s' % (counter,error))
                     counter += 1
                     
                 
             
             
             
             
             
     
      # Replace the following with your code.       
      # print("\n\nThe UE function is not implemented.",
      #     "  Write your own code to implement the UE assignment.\n\n")
      # raise utils.NotYetAttemptedException                  