from flask import Flask, url_for
from flask import render_template
from flask import request, jsonify, Markup
from utility import printHTMLtables
from math import ceil
import pickle
import re   # import xx as y: then you can call functions as y.fName. from xx import fName: then you can call fName directly
#from flask import request
#query = request.args.get(q)    # this is how to get a request for 
#code needed in the HTML: <form method="get">
app = Flask(__name__)

@app.route('/')
def index():   
    return render_template('twinkedIn_home.html') 

@app.route('/about/')   # including the backslash makes the page more robust - ~/about/ will now load as well (otherwise it only finds the page when you type ~/about)
def about():
  return render_template('twinkedIn_about.html')

@app.route('/contacts/')
def contacts(): 
  # load matchDict
  pkl_file = open('matchDict.pkl', 'rb')
  matchDict = pickle.load(pkl_file)
  pkl_file.close()

  # shorten jinja string    
  #linkedInNameListOrdered = matchDict['linkedInNameListOrdered']
  #linkedInNameListOrdered = linkedInNameListOrdered[0:24]
  #matchDict['linkedInNameListOrdered'] = linkedInNameListOrdered

  # print out tables into string
  jinjaStringAndNrOfTablesAndNrOfImages = printHTMLtables(matchDict)
  jinjaString = jinjaStringAndNrOfTablesAndNrOfImages[0]
  nrOfTables = jinjaStringAndNrOfTablesAndNrOfImages[1]
  nrOfImages = jinjaStringAndNrOfTablesAndNrOfImages[2]

  # compute width of scrolling area
  scrollingAreaWidth = 660*nrOfTables     
  print nrOfTables

  # serve up html page with matchDict
  return render_template('twinkedIn_demoBasic_v12.html', 
                        matchDict = matchDict, 
                        jinjaString =Markup(jinjaString),
                        scrollingAreaWidth = scrollingAreaWidth,
                        jinjaTotalNrOfImages = nrOfImages )

@app.route('/api/getMatchDict/',methods = ['POST'])
def getMatchDict():
  # load matchDict
  pkl_file = open('matchDict.pkl', 'rb')
  matchDict = pickle.load(pkl_file)
  pkl_file.close()

  # send to browser
  return jsonify(matchDict)


@app.route('/visualize/')
def visualize():
  return render_template('twinkedIn_demoAdvanced_v4_labels.html')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='192.168.1.14', port=5000)