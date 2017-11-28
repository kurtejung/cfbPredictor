

##http://scikit-learn.org/stable/modules/sgd.html

from sklearn.linear_model import Ridge
import urllib2, re, json
from bs4 import BeautifulSoup
from bs4 import Comment

#### Global Parameters ###

reloadData = False
saveFiles = True
year = 2017
teamList = ['alabama','notre-dame','penn-state','florida-state','texas','purdue','vanderbilt','syracuse','central-florida','oregon','boston-college','michigan','southern-california','stanford','washington','oregon-state','miami-oh','miami-fl','wisconsin','michigan-state','rutgers','ohio-state','oklahoma','iowa-state','tennessee','georgia']
verbose = 0

###########################

teams = {}
win_pct = {}

if reloadData:
      for team in teamList:
            soup = BeautifulSoup(urllib2.urlopen("https://www.sports-reference.com/cfb/schools/{school}/{year}/gamelog/".format(school=team, year=year)).read(),'lxml')
            parsed = soup.find_all("td")
            passTotal = int(parsed[len(parsed)-18].string)
            rushTotal = int(parsed[len(parsed)-15].string)
            turnTotal = int(parsed[len(parsed)-1].string)
            
            record = unicode(soup.find_all("p")[2])
            pattern=re.compile("\d{1,2}")
            wins = int(pattern.findall(record)[0])
            losses = int(pattern.findall(record)[1])
            winPct = float(wins)/float(wins+losses)
            print "wins: ",wins, " losses: ",losses, " win pct: ",winPct
            win_pct.update({team: winPct})
            
            #the defensive stats are protected in a comment
            comments = BeautifulSoup(soup.find_all(string=lambda text:isinstance(text,Comment))[17].string,"lxml")
            parsed = comments.find_all("td")
            defTotal = int(parsed[len(parsed)-18].string) + int(parsed[len(parsed)-15].string)
            turnTotal = int(parsed[len(parsed)-1].string) - turnTotal
            teams.update({team : [passTotal, rushTotal, defTotal, turnTotal]})
            if saveFiles:
                  file = open('{year}/{school}.txt'.format(year=year, school=team),'w')
                  fileContent = [passTotal,rushTotal,defTotal,turnTotal,winPct]
                  json.dump(fileContent,file)
            if verbose:    
                  print "team: ",team, " passTotal: ",passTotal, " rushTotal: ", rushTotal, " defTotal: ", defTotal, " turnTotal: ", turnTotal
	      
else:
      for team in teamList:
            file = open('{year}/{school}.txt'.format(year=year, school=team),'r')
            fileContent = json.load(file)
            teamData = [fileContent[i] for i in range(0,4)]
            win_pct.update({team: fileContent[len(teamData)]})
            teams.update({team : teamData})
            if verbose:
                  print "team: ",team, " passTotal: ",teamData[0], " rushTotal: ", teamData[1], " defTotal: ", teamData[2], " turnTotal: ", teamData[3]
                  print "win pct: ",fileContent[len(teamData)]

#start with 11 teams from this year, hard-coded data
#passing yards, rushing yards, defensive yards allowed, turnover margin, win pct of teams faced
'''
teams = {}
teams.update({'Alabama' : [2466, 3182, 3107, 12, 0.608]})
teams.update({'Notre_Dame' : [2110, 3349, 4400, 5, 0.677]})
teams.update({'Florida_St' : [2114, 1505, 3744, -5, 0.648]})
teams.update({'Texas' : [3198, 1702, 4367, -5, 0.519]})
teams.update({'Purdue' : [2874, 1811, 4468, 3, 0.553]})
teams.update({'Vanderbilt' : [2923, 1291, 4742, -5, 0.583]})
teams.update({'Syracuse' : [3538, 1936, 5328, -12, 0.646]})
teams.update({'UCF' : [3577, 2188, 4389, 17, 0.573]})
teams.update({'Oregon' : [2236, 3216, 4318, 1, 0.573]})
teams.update({'Boston_College' : [1954, 2690, 4775, 8, 0.618]})
teams.update({'Michigan' : [2023, 2236, 3223, -2, 0.565]})

win_pct = {'alabama' : 0.9167, 
'notre-dame' : 0.7500,
'penn-state' : 0.7500,
'florida-state' : 0.4550,
'texas' : 0.500,
'purdue' :  0.500,
'vanderbilt' : 0.417,
'syracuse' : 0.333,
'central-florida' :  1.000,
'oregon' :  0.583,
'boston-college' : 0.583,
'michigan' :  0.667
}
'''

##test teams
Ole_Miss = [3941, 1609, 5514, -5]#, 0.580] #actual .500
TCU = [2856, 2209, 3810, 6]#, 0.529] #actual 0.833
Penn_St = [3430, 2009, 3952, 14]#, 0.585] #actual 0.833

#transform dict to 2D array
teamArr = []
winPctArr = []
for team in teams:
	teamArr.append(teams[team])
	winPctArr.append(win_pct[team])

clf = Ridge(alpha=1.0, normalize="True")
#print teamArr
#print win_pct
clf.fit(X=teamArr, y=winPctArr)

predictPct = clf.predict([Ole_Miss,TCU,Penn_St])

print "Ole Miss: ", predictPct[0], " TCU: ", predictPct[1], " Penn St: ", predictPct[2], '\n'


