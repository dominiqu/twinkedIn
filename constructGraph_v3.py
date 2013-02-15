# constructGraph

# assumes the allNameSearchResults and topHitsFriendsAndFollowers collections have been downloaded into the MongoDB database
from utility import printJSONfile, printGEXFfile
import pymongo
import pickle
import re

# connect 
conn = pymongo.MongoClient()
db = conn.twinkedIn
db.collection_names()

# eliminate screen names with profanities from both databases
allHandles = db.allNameSearchResults.distinct("screen_name")
allHandlesWithContacts = db.topHitsFriendsAndFollowers.distinct("screen_name")
screenNamesToRemove = []
for handle in allHandles:
	if 'shit' in handle or 'fuck' in handle or 'sex' in handle:
		print handle
		if handle not in screenNamesToRemove:
			screenNamesToRemove.append(handle)

for handle in allHandlesWithContacts:
	if 'shit' in handle or 'fuck' in handle or 'sex' in handle:
		print handle
		if handle not in screenNamesToRemove:
			screenNamesToRemove.append(handle)

for screenName in screenNamesToRemove:
	print screenName
	db.allNameSearchResults.remove({"screen_name":screenName})
	db.topHitsFriendsAndFollowers.remove({"screen_name":screenName})

# find all nodes in the allNameSearchResults collection
fullIDList = db.allNameSearchResults.distinct("id")

# go through all friends and followers in topHitsFriendsAndFollowers collection, and see whether any of them are in the full handle list
allHandlesWithContacts = db.topHitsFriendsAndFollowers.distinct("screen_name")

edgeTuplesList = []
edgeNr = 0
for handle in allHandlesWithContacts:
	friendsList = db.topHitsFriendsAndFollowers.find_one({"screen_name":handle})['friends'] # doing this by handles rather than ids because initial DB download had bug on the ids but not handles
	followersList = db.topHitsFriendsAndFollowers.find_one({"screen_name":handle})['followers']
	if friendsList == 'protected': 
		print handle + ' is protected.'
		continue

	for idNr in fullIDList:
		if idNr in friendsList:
			fullListIDnrHandle = db.allNameSearchResults.find_one({"id":idNr})['screen_name']
			print handle + ' is following ' + fullListIDnrHandle + '.'
			edgeNr += 1
			if (handle,fullListIDnrHandle) not in edgeTuplesList: edgeTuplesList.append((handle,fullListIDnrHandle))
		if idNr in followersList:
			fullListIDnrHandle = db.allNameSearchResults.find_one({"id":idNr})['screen_name']
			print fullListIDnrHandle + ' is following ' + handle + '.'
			edgeNr += 1
			if (fullListIDnrHandle,handle) not in edgeTuplesList: edgeTuplesList.append((fullListIDnrHandle,handle))

# print json file
nodeNames = db.allNameSearchResults.distinct("screen_name")
groupList = [1]*len(nodeNames)
JSONlines = printJSONfile(nodeNames,groupList,edgeTuplesList,'twinkedInGraph.json')

# print json file with connected nodes only
newNodeNames = []
for edgeTuple in edgeTuplesList:
	if edgeTuple[0] not in newNodeNames:
		newNodeNames.append(edgeTuple[0])
	if edgeTuple[1] not in newNodeNames:
		newNodeNames.append(edgeTuple[1])
newGroupList = [1]*len(newNodeNames)
newJSONlines = printJSONfile(newNodeNames,newGroupList,edgeTuplesList,'twinkedInGraph_connectedOnly.json')

# print gexf file
weightList = [1]*len(nodeNames)
GEXFlines = printGEXFfile(nodeNames,weightList,edgeTuplesList,'twinkedInGraph.gexf')

# analyze modularity
#1. number of directed edges involved in (store in allNameSearchResults collection)
fullScreenNameList = db.allNameSearchResults.distinct("screen_name")
numberOfDirectedEdgesForEachNode = [0]*len(fullScreenNameList)
for screen_name in fullScreenNameList:
	for edgeTuple in edgeTuplesList:
		if screen_name in edgeTuple:
			numberOfDirectedEdgesForEachNode[fullScreenNameList.index(screen_name)] += 1

# store number of directed edges for each node in database
for screen_name in fullScreenNameList:
	profiles = db.allNameSearchResults.find({"screen_name":screen_name})
	for profile in profiles:
		objectID = profile["_id"]
		screen_name = profile['screen_name']
		numberOfDirectedEdgesInvolvedIn = numberOfDirectedEdgesForEachNode[fullScreenNameList.index(screen_name)]
		profile['numberOfDirectedEdgesInvolvedIn'] = numberOfDirectedEdgesInvolvedIn
		db.allNameSearchResults.update({"_id":objectID}, profile, safe=True)

#2. in-betweenness using networkx
# fill in .......

# store results in matchDict by order of number of edges involved in
cleanNames = db.allNameSearchResults.distinct("linkedInName")
matchDict = {}
for cleanName in cleanNames:
	profiles = db.allNameSearchResults.find({"linkedInName":cleanName}).sort([("numberOfDirectedEdgesInvolvedIn",-1), ("hitNr", 1)])
	orderedScreenNameList = []
	for profile in profiles:
		if profile['numberOfSearchResults'] == 0 or profile['numberOfSearchResults'] == 100:
			continue
		orderedScreenNameList.append(profile['screen_name'])
		print cleanName + ': ' + orderedScreenNameList[-1] + ': ' + str(profile['numberOfDirectedEdgesInvolvedIn'])
	matchDict[cleanName] = orderedScreenNameList

# get ordered list of the keys based on relevance of first screen_name associated with each cleanName
relevanceMetric = []
linkedInNameList = []
for key in matchDict: 
	linkedInNameList.append(key)
	if len(matchDict[key])==0:
		relevanceMetric.append(-1)
	else:
		relevanceMetric.append( db.allNameSearchResults.find_one({"screen_name":matchDict[key][0]})['numberOfDirectedEdgesInvolvedIn']    )

linkedInNameListOrdered = [x for (y,x) in sorted(zip(relevanceMetric,linkedInNameList), reverse=True)]
matchDict['linkedInNameListOrdered'] = linkedInNameListOrdered

# pickle the matchDict
output = open('matchDict.pkl', 'wb')
pickle.dump(matchDict, output)
output.close() 

# unpickle the matchDict
'''
pkl_file = open('matchDict.pkl', 'rb')
matchDict = pickle.load(pkl_file)
pkl_file.close()
'''

# show hit numbers of first in list
'''
counter = 0
totalHits = 0
for key in matchDict:
	if len(matchDict[key])>0:
		thisHitNr = db.allNameSearchResults.find_one({"screen_name":matchDict[key][0]})['hitNr']
		counter += 1
		totalHits += thisHitNr
float(totalHits)/float(counter)
'''

# store results in matchDict by order of modularity






