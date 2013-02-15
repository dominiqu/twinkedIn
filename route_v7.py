from flask import Flask, url_for
from flask import render_template
from flask import request, jsonify
import pickle
import re   # import xx as y: then you can call functions as y.fName. from xx import fName: then you can call fName directly
#from flask import request
#query = request.args.get(q)    # this is how to get a request for 
#code needed in the HTML: <form method="get">
app = Flask(__name__)

def loadConciseData():
  topLinkedInNodes = open('./static/json/topLinkedInNodes.txt').read().splitlines()
  topLinkedInNodes = [int(x) for x in topLinkedInNodes]

  topLinkedInNodes_screenName = open('./static/json/topLinkedInNodes_screenName.txt').read().splitlines()
  topLinkedInNodes_fullName = open('./static/json/topLinkedInNodes_fullName.txt').read().splitlines()

  return {'topLinkedInNodes':topLinkedInNodes, 'topLinkedInNodes_screenName': topLinkedInNodes_screenName, 'topLinkedInNodes_fullName': topLinkedInNodes_fullName}

@app.route('/')
def index(): 
    return render_template('twinkedIn_home.html') 

@app.route('/about/')   # including the backslash makes the page more robust - ~/about/ will now load as well (otherwise it only finds the page when you type ~/about)
def about():
  return render_template('twinkedIn_about.html')

@app.route('/demo/')
def contacts():
  # load matchDict
  pkl_file = open('matchDict.pkl', 'rb')
  matchDict = pickle.load(pkl_file)
  pkl_file.close()

  # get top 5 names
  linkedInNameListOrdered = matchDict['linkedInNameListOrdered']
  contact_name_instances = linkedInNameListOrdered[0:6]
  screen_name_instances = []
  firstName_instances = []
  for linkedInName in contact_name_instances:
    screen_name_instances.append(matchDict[linkedInName][0])
    firstName_instances.append(re.match(r'(\w+)',linkedInName).group(1))

  #for x in topLinkedInNodes:
  #  print twitterSoup_AllCandidates[x][0]
  #  print twitterSoup_AllCandidates[x][2]['profile_image_url_https']

  return render_template('twinkedIn_demoBasic_v10.html', 
  					contact_name=contact_name_instances,
  					screen_name= screen_name_instances,
            firstName = firstName_instances)

@app.route('/api/updateNames/',methods = ['POST'])
def updateNames():
  #print 'hello'
  #print request.method
  #name = request.form
  currentFirstName = request.json['currentFirstName']
  currentFullName = request.json['currentFullName']
  currentTwitterHandle = request.json['currentTwitterHandle']
  rejectedTwitterHandles = request.json['rejected_TwitterHandles']

  print 'Current first name: ' + currentFirstName
  print 'Current full name: ' + currentFullName
  print 'Current Twitter handle: ' + currentTwitterHandle
  print 'Rejected Twitter handles: ' 
  for item in rejectedTwitterHandles:
    print item

  # load matchDict
  pkl_file = open('matchDict.pkl', 'rb')
  matchDict = pickle.load(pkl_file)
  pkl_file.close()

  temp = matchDict['linkedInNameListOrdered']
  topLinkedInNodes = []
  topLinkedInNodes_screenName = []
  topLinkedInNodes_fullName = []
  for name in temp:
    if len(matchDict[name])>0:
      topLinkedInNodes.append(name)
      topLinkedInNodes_screenName.append(matchDict[name][0])
      topLinkedInNodes_fullName.append(name)

  # get first one in the list that isn't in rejectedTwitterHandles
  for key in range(0,len(topLinkedInNodes),1):
    print 'Next most influential candidate in list: ' + topLinkedInNodes_screenName[key]
    if topLinkedInNodes_screenName[key] not in rejectedTwitterHandles:
      newScreenName = topLinkedInNodes_screenName[key]
      newFullName = topLinkedInNodes_fullName[key] #twitterSoup_AllCandidates[key][2]['name']
      newFirstName = re.match(r'(\w+)',newFullName).group(1)
      break
  
  #newScreenName = "seamusabshere"
  #newFirstName = "Seamus"
  #newFullName = "Seamus Abshere"

  #newScreenName = "dvdsompel"
  #newFirstName = "Dominique"
  #newFullName = "Van de Sompel"


  # do stuff, make a dictionary as a return argument
  newNamesDIct = {'newScreenName':newScreenName, 'newFirstName':newFirstName, 'newFullName':newFullName}
  return jsonify(newNamesDIct)


@app.route('/advanced/')
def advanced():
  return render_template('twinkedIn_demoAdvanced_v3_labels.html')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='192.168.1.14', port=5000)