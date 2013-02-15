# build database for each user. For each database, we will have two collections:
# 1. allNameSearchResults: the results of all name searches on Twitter
# 2. friendsAndFollowers: the friends and followers of the first-hit subset of allNameSearchResults

# main_getData.py
from utility import setUpLinkedInClient, setUpTwitterClient, getLinkedInContacts, cleanUpNamesOfLinkedInContacts, searchNamesOnTwitterAndStoreInMongoDB, searchFirstHitFriendsAndFollowersAndStoreInMongoDB
import pymongo

# set up LinkedIn and Twitter clients
linkedInClient = setUpLinkedInClient()
twitterClient = setUpTwitterClient()

# get authenticating user's LinkedIn contacts
allLinkedInContacts = getLinkedInContacts(linkedInClient)
cleanNames = cleanUpNamesOfLinkedInContacts(allLinkedInContacts)

# search all LinkedIn contacts on Twitter and store into MongoDB database (as 'allNameSearchResults' collection)
searchNamesOnTwitterAndStoreInMongoDB(twitterClient,cleanNames)

# search for friends and followers of all first and second hits in 'allNameSearchResults' collection and store into MongoDB database (as 'firstHitFriendsAndFollowers' collection)
searchFirstHitFriendsAndFollowersAndStoreInMongoDB(twitterClient)




# check whether database storage really worked
'''
conn = pymongo.MongoClient()
conn.database_names()
db = conn.twinkedIn
db.collection_names()
db.allNameSearchResults.find().count()
db.allNameSearchResults.find({"numberOfSearchResults": {"$gt": 20}}).count()
db.allNameSearchResults.find({"numberOfSearchResults": 20}).count()
singleHits = db.allNameSearchResults.find({"numberOfSearchResults": {"$in": [1]}  })
for hit in singleHits:
	print hit['linkedInName'] + ": " + hit['screen_name']
	print hit['screen_name'] in firstHitHandles

# compute a histogram
nrOfSrchReslts = []
for cleanName in cleanNames:
	cursor = db.allNameSearchResults.find_one({"linkedInName": cleanName })
	nr = cursor['numberOfSearchResults']
	if nr==100:
		nr = 20
	nrOfSrchReslts.append(nr)
'''	 	

###############################################################
############# START NEW FILE: GRAPH BUILDER ###################
###############################################################

### Rate limits:
# temp4 = twitterClient.followers.ids(screen_name='akuhn')
# rate limit: 15/15 mins, but get up to 5000 ids/show

# temp5 = twitterClient.friends.ids(screen_name='akuhn')
# rate limit: 15/15 mins, but get up to 5000 ids/show

# temp3 = twitterClient.statuses.user_timeline(screen_name='ay_shake')
# gets last 200 tweets for a user (have to set a 'count=200' argument). For each: mentions, text, hashtags, number of retweets, number of tweets, number of followers, number of following, whether user protected info
# rate limit: 180/15 mins

