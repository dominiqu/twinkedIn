# utilities
import oauth2 as oauth
import httplib2
from twitter import *
import simplejson 
import re
import unicodedata
import pymongo
import time
from datetime import datetime
from datetime import timedelta
from math import floor, ceil

def setUpLinkedInClient():
	# specify keys (consumer: our app. user: the person logging into LinkedIn via our app (LinkedIn then gives us a placeholder user_token and user_secret to represent that user, without giving us the actual name and password of the user - although of course the username can be queried for later))
	consumer_key     =   'uszh5pfeb54o'     # this is the API key  (the 'username' of my app when talking to LinkedIn)
	consumer_secret  =   'pZsNH8d3omOpzrka' # this is the API secret (the 'password' of my app when talking to LinkedIn)
	user_token       =   '1802fb97-fc3a-4dff-904a-647d989784db'  # OAuth User Token: this is the 'username' for the user that signed into the app 
	user_secret      =   '8ad8d623-0655-48c8-869d-bcf45e3426ea'  # OAuth User secret: this is the 'password' for the user that signed into the app 
	 
	# Use your API key and secret to instantiate consumer object (consumer object = the app = api client)
	consumer = oauth.Consumer(consumer_key, consumer_secret)
	 
	# Use your developer token and secret to instantiate access token object
	access_token = oauth.Token(key=user_token,secret=user_secret)
	client = oauth.Client(consumer, access_token)

	return client

def setUpTwitterClient():
	# specify keys (consumer: our app. user: the person logging into LinkedIn via our app (LinkedIn then gives us a placeholder user_token and user_secret to represent that user, without giving us the actual name and password of the user - although of course the username can be queried for later))
	consumer_key = 'FBJuTrqQWlltW23FbthcTA'
	consumer_secret = 'NNUVmwKbV6GIIkCFON6qAMuIwaFpxaEdsylWEnCE'
	user_token       =   '1120675440-wCc8TXO3xF1D3li68yZI66ypJ68pYrQ4H8yRicu'  # OAuth User Token: this is the 'username' for the user that signed into the app 
	user_secret      =   'aaBKw61p9YR4mWDZwx2HTSjMeeZJtldcEk7RcWmaVPg'  # OAuth User secret: this is the 'password' for the user that signed into the app 

	# see "Authentication" section below for tokens and keys
	t = Twitter( auth=OAuth(user_token, user_secret, consumer_key, consumer_secret) )
	return t

def getLinkedInContacts(client):
	urlRoot = 'http://api.linkedin.com/v1/people/'
	jsonFormat = '?format=json' 
	resp,content = client.request(urlRoot+'~/connections:(id,first-name,last-name,headline,site-standard-profile-request)'+jsonFormat, 'GET', '')
	allLinkedInContacts = simplejson.loads(content)  # convert json into Python dict
	allContacts = []
	for contact in allLinkedInContacts['values']:
		allContacts.append(contact['firstName'] + ' ' + contact['lastName'])
	return allContacts

def cleanUpNamesOfLinkedInContacts(allLinkedInContacts):
	cleanNames = []
	for contact in allLinkedInContacts:
		if re.search('private',contact): 
			continue

		name = contact
		name = re.sub('\(.*\)', '', name)
		name = re.sub('\(.*\)', '', name)
		name = re.sub('^M\.','',name)
		name = re.sub('^Mr\.','',name)
		name = re.sub('^Mrs\.','',name)
		name = re.sub('^Ms\.','',name)
		name = re.sub('^Dr\.','',name)
		name = re.sub('^Igr\.','',name)
		name = re.sub('^M ','',name)
		name = re.sub('^Mr ','',name)
		name = re.sub('^Mrs ','',name)
		name = re.sub('^Ms ','',name)
		name = re.sub('^Dr ','',name)
		name = re.sub('^Igr ','',name)
		name = re.sub(',.*','',name)
		
		# get rid of initials
		name = re.sub(' \w\.\w\.\w\.','',name)
		name = re.sub(' \w\.\w\.','',name)
		name = re.sub(' \w\.','',name)

		# get rid of question marks
		#name = re.sub('?','',name)
		
		# get rid of leading and trailing white spaces 
		name = name.strip()

		# get rid of accents (using code I found online)
		if type(name)==unicode:
			name = unicodedata.normalize( "NFKD", name ).encode('ASCII', 'ignore')
		else:
			name = unicodedata.normalize( "NFKD", name.decode('utf-8') ).encode('ASCII', 'ignore')

		# append name
		cleanNames.append(name)
	return cleanNames

def checkWhetherLinkedInandTwitterMatch(linkedInName,twitterName):
	# get rid of accents 
	twitterName = twitterName.replace(u'\u0142','l')
	twitterName = twitterName.replace(u'\xe9','e')
	twitterName = twitterName.replace(u'\xf3','o')

	# get rid of further accents (using code I found online)
	if type(twitterName)==unicode:
		twitterName = unicodedata.normalize( "NFKD", twitterName ).encode('ASCII', 'ignore')
	else:
		twitterName = unicodedata.normalize( "NFKD", twitterName.decode('utf-8') ).encode('ASCII', 'ignore')

	# get rid of punctuation
	twitterName = twitterName.replace('.','')
	twitterName = twitterName.replace('-',' ')

	# tidy up spaces at the extremes of the Twitter string
	twitterName = twitterName.strip()

	if linkedInName.lower() == twitterName.lower():
		return True

	if linkedInName.lower().replace(' ','') == twitterName.lower().replace(' ',''):
		return True

	# check whether twitterName is alphanumeric. If not, reject
	temp = twitterName
	flag = temp.replace(' ', '').isalnum()
	if flag == False:
		return False

	# split Twitter name into components
	temp = twitterName
	temp = temp.split(' ')

	# check whether each part of the Twitter name is in the LinkedIn name (if so, return true)
	count = 0
	for namePart in temp:
		if namePart.lower() in linkedInName.lower().split(' '):
			count += 1
		
	# if all match, or at least two out of more, declare a match	
	if len(temp) == count:
		return True
	elif len(linkedInName.split(' ')) == count:
		return True
	elif len(temp) > 2 and count >= 2:
		return True
	else:
		return False

def searchNamesOnTwitterAndStoreInMongoDB(twitterClient,cleanNames):

	# connect to mongoDB database (make sure mongodb is running - it's the server process that runs the database on local host)
	conn = pymongo.Connection()
	db = conn.twinkedIn
	allNameSearchResults = db.allNameSearchResults
	db.allNameSearchResults.remove() # make sure we're starting from scratch so no silly duplicates
	allNameSearchResults = db.allNameSearchResults  

	# search all names on Twitter and enter results into MongoDB database
	cleanNamesNotFound = []
	count = 1
	waitPeriodInSeconds = 15*60+5 # add 5 seconds just in case...
	for cleanName in cleanNames:
		# perform the search (wait first if rate limit exceeded)
		print ' '
		print 'Searching LinkedIn contact nr. ' + str(count) + ': ' + cleanName
		try:
			twitterSearchJSONstring = twitterClient.users.search(q=cleanName,page=1,per_page=20,include_entities='true')
		except:
			print 'Rate limit exceed at ' + datetime.now().strftime('%H:%M:%S') +'. Waiting for ' + str(float(waitPeriodInSeconds)/float(60)) + ' minutes until ' + (datetime.now() + timedelta(float(waitPeriodInSeconds)/float(24*60*60))).strftime('%H:%M:%S') + '...'
			time.sleep(waitPeriodInSeconds)
			twitterSearchJSONstring = twitterClient.users.search(q=cleanName,page=1,per_page=20,include_entities='true')
		
		# determine number of search results
		numberOfSearchResults = len(twitterSearchJSONstring)

		# deal with case of zero search results 
		if numberOfSearchResults == 0:
			print cleanName + ' not found.'
			hitNr = 0
			enrichedJSONstring = {'linkedInName':cleanName,'hitNr':hitNr,'numberOfSearchResults':numberOfSearchResults}
			allNameSearchResults.insert(enrichedJSONstring)
			cleanNamesNotFound.append(cleanName)
			
			count = count + 1
			continue
		
		# deal with case of 1 or more search results 
		hitNr = 0
		cleanHitNr = 0
		linkedInName = cleanName
		for twitterProfile in twitterSearchJSONstring:

			# store Twitter profile if Twitter name is a reasonable match to the LinkedIn name
			twitterName = twitterProfile['name']
			if checkWhetherLinkedInandTwitterMatch(linkedInName,twitterName) == False:
				print linkedInName + ' : ' + twitterName + ' does not match.'
				hitNr += 1
				continue
			else:
				print linkedInName + ' : ' + twitterName + ' match.'
				hitNr += 1
				cleanHitNr += 1
				enrichedJSONstring = twitterProfile
				enrichedJSONstring['linkedInName'] = cleanName
				enrichedJSONstring['hitNr'] = hitNr
				enrichedJSONstring['numberOfSearchResults'] = numberOfSearchResults
				allNameSearchResults.insert(enrichedJSONstring)

		if cleanHitNr == 0:
			print 'No clean Twitter name matches found for ' + cleanName + '.'
			enrichedJSONstring = {'linkedInName':cleanName,'hitNr':cleanHitNr,'numberOfSearchResults':100}
			allNameSearchResults.insert(enrichedJSONstring)
			cleanNamesNotFound.append(cleanName)
		else:
			print 'Found ' + str(cleanHitNr) + ' clean hits for ' + cleanName + '.'
			
		count = count + 1	
	return cleanNamesNotFound

def searchFirstHitFriendsAndFollowersAndStoreInMongoDB(twitterClient):
	# connect to mongoDB database (make sure mongodb is running - it's the server process that runs the database on local host)
	conn = pymongo.Connection()
	db = conn.twinkedIn
	topHitsFriendsAndFollowers = db.topHitsFriendsAndFollowers
	db.topHitsFriendsAndFollowers.remove() # make sure we're starting from scratch so no silly duplicates
	topHitsFriendsAndFollowers = db.topHitsFriendsAndFollowers  

	# determine the handles of the top 2 hits
	cleanNames = db.allNameSearchResults.distinct("linkedInName")
	topHitHandles = []
	topHitIDs = []
	for cleanName in cleanNames:
		cursor = db.allNameSearchResults.find({"linkedInName":cleanName}).sort("hitNr")
		if 'screen_name' in cursor[0]:
		 	print cursor[0]['screen_name'] + '(hitNr: ' + str(cursor[0]['hitNr']) + ').'
		 	topHitHandles.append(cursor[0]['screen_name'])
		 	topHitIDs.append(cursor[0]['id'])
		 	if cursor.count()>1:
		 		topHitHandles.append(cursor[1]['screen_name'])
		 		topHitIDs.append(cursor[1]['id'])

	# start searching...
	waitPeriodInSeconds = 15*60+5 # add 5 seconds just in case...
	count = 1
	for handle in topHitHandles:
		print 'Searching for friends and followers of top hit candidate ' + str(count) + ' of ' + str(len(topHitHandles)) + ' (@' +  handle + ')...'
		JSONstring = db.allNameSearchResults.find({"screen_name":handle})
		twitterProfile = JSONstring[0]

		# take care of case where candidate id is protected (doesn't share tweets or follows or following)
		if twitterProfile['protected']:
			enrichedJSONstring = {'screen_name':handle, 'id':topHitIDs[count-1], 'friends':'protected', 'followers': 'protected'}
			topHitsFriendsAndFollowers.insert(enrichedJSONstring)	
		else:
			try:
				idsFollowing = twitterClient.friends.ids(screen_name=handle)
				idsFollowers = twitterClient.followers.ids(screen_name=handle)
			except:
				print 'Rate limit exceed at ' + datetime.now().strftime('%H:%M:%S') +'. Waiting for ' + str(float(waitPeriodInSeconds)/float(60)) + ' minutes until ' + (datetime.now() + timedelta(float(waitPeriodInSeconds)/float(24*60*60))).strftime('%H:%M:%S') + '...'
				time.sleep(waitPeriodInSeconds)
				idsFollowing = twitterClient.friends.ids(screen_name=handle)
				idsFollowers = twitterClient.followers.ids(screen_name=handle)
			enrichedJSONstring = {'screen_name':handle, 'id':topHitIDs[count-1], 'friends':idsFollowing['ids'], 'followers': idsFollowers['ids']}
			topHitsFriendsAndFollowers.insert(enrichedJSONstring)

		count += 1
	return 0

def printJSONfile(nodeNames,groupList,edgeTuplesList,fileName):
	# print out node list
	JSONlines = []
	JSONlines.append('{')
	JSONlines.append('    "nodes":[')
	for nodeName in nodeNames:
		JSONlines.append('      {"name":"'+ nodeName + '","group":' + str(groupList[nodeNames.index(nodeName)]) + '},')   # choose item rather than twitterSoup[item][0]['name'] because the former is the LinkedIn name and usually better maintained (i.e. with capital letters)	
	JSONlines[-1] = '      {"name":"'+ nodeName + '","group":' + str(groupList[nodeNames.index(nodeName)]) + '}'   
	JSONlines.append('],')

	# print edge info ({"source":nodeNr,"target":targetNr,"value":1},)
	JSONlines.append('  "links":[')
	for edgeTuple in edgeTuplesList:
		JSONlines.append('{"source":' + str(nodeNames.index(edgeTuple[0])) + ',"target":' + str(nodeNames.index(edgeTuple[1])) + ',"value":1},')
	JSONlines[-1] = '{"source":' + str(nodeNames.index(edgeTuple[0])) + ',"target":' + str(nodeNames.index(edgeTuple[1])) + ',"value":1}'
	JSONlines.append('    ]')
	JSONlines.append('}')

	# print contents into JSON file
	f = open('./static/json/' + fileName, 'w')
	for item in JSONlines:
	   f.write("%s\n" % item)
	f.close()

	return JSONlines


def printGEXFfile(nodeNames,weightList,edgeTuplesList,fileName):
	GEXFlines = []
	GEXFlines.append('<?xml version="1.0" encoding="UTF-8"?>')
	GEXFlines.append('<gexf xmlns:viz="http:///www.gexf.net/1.1draft/viz" version="1.1" xmlns="http://www.gexf.net/1.1draft">')
	GEXFlines.append('<meta lastmodifieddate="2010-03-03+23:44">')
	GEXFlines.append('<creator>Gephi 0.7</creator>')
	GEXFlines.append('</meta>')
	GEXFlines.append('<graph defaultedgetype="directed" idtype="string" type="static">')
	GEXFlines.append('<nodes count="' + str(len(nodeNames)) + '">')
	idNr = 0
	for nodeName in nodeNames:
		GEXFlines.append('<node id="' + str(idNr) + '" label="' + nodeName + '"/>')
		idNr += 1
	GEXFlines.append('</nodes>')
	GEXFlines.append('<edges count="' + str(len(edgeTuplesList)) + '">')
	edgeNr = 0
	for edgeTuple in edgeTuplesList:
		GEXFlines.append('<edge id="' + str(edgeNr) + '" source="' + str(nodeNames.index(edgeTuple[0])) + '" target="' + str(nodeNames.index(edgeTuple[1])) + '" weight="' + str(weightList[nodeNames.index(nodeName)]) + '"/>')
		edgeNr += 1
	GEXFlines.append('</edges>')
	GEXFlines.append('</graph>')
	GEXFlines.append('</gexf>')

	# print contents into JSON file
	f = open('./static/json/' + fileName, 'w')
	for item in GEXFlines:
	   f.write("%s\n" % item)
	f.close()

	return GEXFlines

def printHTMLtables(matchDict):
	# get names in order of importance
	linkedInNameListOrdered = matchDict['linkedInNameListOrdered']

	# generate list of first names:
	firstNamesOrdered = []
	for name in linkedInNameListOrdered:
		firstNamesOrdered.append(re.match(r'(\w+)',name).group(1))

	# create new matchDict with only names that have at least one hit
	newMatchDict = {}
	for name in linkedInNameListOrdered:
		if len(matchDict[name])>0:
			newMatchDict[name] = matchDict[name]

	# print out tables, six images at a time, in rows of three
	count = 1;
	nrOfImages = len(newMatchDict)
	nrOfTables = int(ceil(    float(len(newMatchDict)-1)/float(6)    ))
	tableList = range(1,nrOfTables+1,1) 
	rowList = [1,2]
	colList = [1,2,3]

	jinjaString = ''
	for table in tableList:
		jinjaString +=  '<table style="display: inline-block; float: left; ">'
		
		for row in rowList:
			jinjaString +=  '<tr>'

			for col in colList:
				jinjaString +=  '<td>'
				if count <(len(linkedInNameListOrdered)+1):
					jinjaString +=  '<div>'
					jinjaString +=  '<img id="twitImg_slot' + str(count) + '" class="croppedImage" src="https://api.twitter.com/1/users/profile_image?screen_name=' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '&size=original" title="@' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '">'
					jinjaString +=  '</div>'
					jinjaString +=  '<div id="slot' + str(count) + '" style="text-align: center; color:white; font: 15px/30px Helvetica, sans-serif;">'
					jinjaString +=  linkedInNameListOrdered[count-1]
					jinjaString +=  '</div>'
					jinjaString +=  '<div style="text-align: center;">'
					jinjaString +=  '<span id="twitterButton' + str(count) + '"><a href="https://twitter.com/' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '" class="twitter-follow-button" data-show-count="false" data-size="small">Follow @' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '</a></span>'
					jinjaString +=  '<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>'
					jinjaString +=  '</div>'
					jinjaString +=  '<div id="allTextUnderNeathImage' + str(count) + '" style="text-align: center; margin-top: -7px; margin-bottom: 2px">'
					#jinjaString +=  '<span><a id="buttonNr' + str(count) + '" class = "textButton" onClick="myFunction_slot(this);" style="text-align: center;">Different <span id="buttonFirstName' + str(count) + '">' + firstNamesOrdered[count-1] + '</span>?</a></span><span style="font-size: 6pt;"> | </span><span><a id="buttonNrb' + str(count) + '" class = "textButton" onClick="myFunction_slotBack(this);" style="text-align: center;">back</a></span>'
					jinjaString +=  '<span><a id="buttonNr' + str(count) + '" class = "textButton" onClick="myFunction_forward(this);" style="text-align: center;">Different <span id="buttonFirstName' + str(count) + '">' + firstNamesOrdered[count-1] + '</span>?</a></span>'
					jinjaString +=  '<span id="printUndoTextButton' + str(count) + '"></span>'
					jinjaString +=  '</div>'
				count += 1
				jinjaString +=  '</td>'

			jinjaString +=  '</tr>'
		jinjaString +=  '</table>'


	jinjaStringAndNrOfTables = [jinjaString,nrOfTables,nrOfImages]	
	return jinjaStringAndNrOfTables