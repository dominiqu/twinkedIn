import pickle
from numpy import floor
from utility import printHTMLtables

# load matchDict
pkl_file = open('matchDict.pkl', 'rb')
matchDict = pickle.load(pkl_file)
pkl_file.close()

jinjaString = printHTMLtables(matchDict)




for table in tableList:
	print '<table style="display: inline-block; float: left; ">'
	
	for row in rowList:
		print '<tr>'

		for col in colList:
			print '<td>'
			print '<div>'
			print '<img id="twitImg_slot' + str(count) + '" class="croppedImage" src="https://api.twitter.com/1/users/profile_image?screen_name=' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '&size=original" title="@' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '">'
			print '</div>'
			print '<div style="text-align: center; color:white; font: 15px/30px Helvetica, sans-serif;">'
			print linkedInNameListOrdered[count-1]
			print '</div>'
			print '<div style="text-align: center;">'
			print '<a href="https://twitter.com/' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '" class="twitter-follow-button" data-show-count="false" data-size="small">Follow @' + newMatchDict[linkedInNameListOrdered[count-1]][0] + '</a>'
			print '<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>'
			print '</div>'
			print '<div style="text-align: center; margin-top: 5px;">'
			print '<a id="buttonNr' + str(count) + '" class = "textButton" onClick="myFunction_slot(this);" style="text-align: center;">Different <span id="buttonFirstName' + str(count) + '">' + linkedInNameListOrdered[count-1] + '</span>?</a>'
			print '</div>'
			count += 1
			print '</td>'

		print '</tr>'
	print '</table>'



# take care of left overs (Done in final code!)

