# -*- coding: iso-8859-15 -*-
import os, sys
import oauth2 as oauth
import xml.etree.ElementTree as ET
import heapq

# Fill the keys and secrets you retrieved after registering the app with Linkedin
consumer_key     =   '7594vxig51bv1m'
consumer_secret  =   'ZRYPhPer2L2Nd421'
user_token       =   '9048ffef-c28d-42f9-8233-85bf4a8f2d25'
user_secret      =   '44af98cc-32e7-45d1-b419-501027a41490'

# Numbers top and botom connection for output
N_TOP	= 25
N_BOTOM = 25

# Multiplicators:
MULT_1    = 1
MULT_2    = 100

OUT_FORMAT = '{0:3d}: {1:25s} {2:4d}  ({3:3d}, {4:3d})'

requestConnection = "https://api.linkedin.com/v1/people/~/connections:(first-name,last-name,id)"
requestNumConnect = "https://api.linkedin.com/v1/people/{id}/num-connections"
requestRelatedCon = "https://api.linkedin.com/v1/people/id={id}:(relation-to-viewer:(num-related-connections))"
#requestRelatedCon = "https://api.linkedin.com/v1/people/{id}/relation-to-viewer:(related-connections:(id,first-name,last-name,distance))"
#Following fields are also avalable for any {id}: "specialties", "location", "positions"

# Error codes:
ERR_OK               = 0
ERR_LINKEDIN_REQUEST = 1



class ConnectionHeap:
        def __init__(self, nMax):
                self.nElemMax = nMax
		self.nElem = 0
		self.heap = []

	def processConnection(self, connection):
	    if self.nElem == self.nElemMax:
                # Heap is full, check the possibility to replace one of the element
		if connection[0] <= self.heap[0][0]:
		    return connection

		# Remove worst element from the heap 
                # (perhaps, we will add it to the bottom connections heap)
                retVal = heapq.heappop(self.heap)
	    else:
		retVal = None
		self.nElem = self.nElem + 1

	    # Add connection to te heap
            heapq.heappush(self.heap, connection)
	    return retVal

	def printTopConnections(self, idx = 1):
	    lenHeap = len(self.heap)
	    print "Top " + str(lenHeap) + " connections:"

            # Move information from heap to the ordered array of connections
            conArray = []
	    for i in range (0, lenHeap):
		conArray.append(heapq.heappop(self.heap))

	    for i in range (0, lenHeap):
                con = conArray[lenHeap - i - 1]
        	print OUT_FORMAT.format(idx + i, con[1].encode('utf8'), con[0], int(con[2]), int(con[3]))

	def printBotConnections(self, idx):
	    lenHeap = len(self.heap)
	    print "Bottom " + str(lenHeap) + " connections:"
	    for i in range (0, lenHeap):
		con = heapq.heappop(self.heap)
        	print OUT_FORMAT.format(idx + i, con[1].encode('utf8'), -con[0], int(con[2]), int(con[3]))


# Function to check status of Linked API responce
def checkStatus(resp, request, content, exit = 1):
    if resp["status"]  == "200":
	return ERR_OK

    print content
    print "Something wrong with the request: '" + request + "'"
    if exit:
        raise SystemExit

    return ERR_LINKEDIN_REQUEST

#
# MAIN PROGRAM:
#
# Use your API key and secret to instantiate consumer object
consumer = oauth.Consumer(consumer_key, consumer_secret)
 
# Use the consumer object to initialize the client object
client = oauth.Client(consumer)
 
# Use your developer token and secret to instantiate access token object
access_token = oauth.Token(key=user_token, secret=user_secret)
 
client = oauth.Client(consumer, access_token)
 
# Make call to LinkedIn to retrieve your own profile
resp,content = client.request(requestConnection, "GET", "")
checkStatus(resp, requestConnection, content)

# Load XML for parsing
root = ET.fromstring(content)

# Create heaps for top/bottom connections
topConnections = ConnectionHeap(N_TOP)
botConnections = ConnectionHeap(N_BOTOM)

numCon = 0
# Loop over all personal first degree connections
for person in root.iter('person'):

    # For each person:
    #   a) Find the number of his/her first degree connections:
    linkedin_id = person.find('id').text
    if linkedin_id == 'private':
        continue

    request = requestNumConnect.format(id = linkedin_id)
    resp, content = client.request(request, "GET", "")
    if checkStatus(resp, request, content, 0) != ERR_OK:
        continue

    rank_1 = int(ET.fromstring(content).text)

    # and
    #   b) Find the number of shared connections:
    request = requestRelatedCon.format(id = linkedin_id)
    resp, content = client.request(request, "GET", "")
    if checkStatus(resp, request, content, 0) != ERR_OK:
        continue

    rank_2 = ET.fromstring(content).find("relation-to-viewer").find("num-related-connections")

    if rank_2 is None:
        continue

    numCon = numCon + 1
    rank_2 = int(rank_2.text)

    # Combine ranks
    rank = MULT_1 * rank_1 + MULT_2 * rank_2
    connectionName = person.find('first-name').text + " " + person.find('last-name').text

    # Create the tuple from (rank, name, rank_, rank_2) and try to add it the topConnections heap 
    con = topConnections.processConnection((rank, connectionName, rank_1, rank_2)) 

    # The connection, returned on previous step, try to add to the botConnections heap
    if con != None:
        botConnections.processConnection((-int(con[0]), con[1], con[2], con[3]))


# Make output of top/bottom connections 
topConnections.printTopConnections(1)
print ". . . . "
botConnections.printBotConnections(numCon - len(botConnections.heap) + 1)

#<message>Throttle limit for calls to this resource is reached.</message>

