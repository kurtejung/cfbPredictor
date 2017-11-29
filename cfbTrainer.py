
##http://scikit-learn.org/stable/modules/sgd.html

from sklearn.linear_model import Ridge, SGDRegressor
import urllib2, re, json
from bs4 import BeautifulSoup
from bs4 import Comment

#### Global Parameters ###

reloadData = False
saveFiles = True
year = 2017
teamList = []

doPower5 = True
doAll = False

verbose = 1

###########################

teams = {}
win_pct = {}

##hardcode all teams by conference for easy loading
teamListAAC = ['central-florida','south-florida','temple','east-carolina','cincinnati','connecticut','memphis','houston','navy','southern-methodist','tulane','tulsa']
teamListACC = ['clemson','north-carolina-state','wake-forest','boston-college','louisville','florida-state','syracuse','miami-fl','virginia-tech','georgia-tech','pittsburgh','virginia','duke','north-carolina']
teamListBigTwelve = ['oklahoma','texas-christian','oklahoma-state','texas','west-virginia','kansas-state','iowa-state','texas-tech','baylor','kansas']
teamListBigTen = ['ohio-state','penn-state','michigan-state','michigan','rutgers','maryland','indiana','wisconsin','northwestern','purdue','iowa','nebraska','minnesota','illinois']
teamListCUSA = ['florida-atlantic','florida-international','marshall','western-kentucky','middle-tennessee-state','old-dominion','charlotte','north-texas','alabama-birmingham','southern-mississippi','louisiana-tech','texas-san-antonio','rice','texas-el-paso']
teamListInd = ['massachusetts','notre-dame','army','brigham-young']
teamListMAC = ['akron','ohio','miami-oh','buffalo','bowling-green-state','kent-state','toledo','central-michigan','northern-illinois','western-michigan','eastern-michigan','ball-state']
teamListMWC = ['boise-state','wyoming','colorado-state','air-force','utah-state','new-mexico','fresno-state','san-diego-state','nevada-las-vegas','nevada','hawaii','san-jose-state']
teamListPACTwelve = ['stanford','washington','washington-state','oregon','california','oregon-state','southern-california','arizona-state','arizona','ucla','utah','colorado']
teamListSEC = ['georgia','south-carolina','kentucky','missouri','florida','vanderbilt','tennessee','auburn','alabama','louisiana-state','mississippi-state','texas-am','mississippi','arkansas']
teamListSunBelt = ['troy','arkansas-state','appalachian-state','georgia-state','louisiana-lafayette','louisiana-monroe','new-mexico-state','south-alabama','idaho','georgia-southern','coastal-carolina','texas-state']

if doAll:
      doPower5 = True
      for team in teamListAAC: teamList.append(team)
      for team in teamListCUSA: teamList.append(team)
      for team in teamListMAC: teamList.append(team)
      for team in teamListMWC: teamList.append(team)
      for team in teamListSunBelt: teamList.append(team)
      teamList.append('massachusetts')
      teamList.append('army')
      teamList.append('brigham-young')

if doPower5:
      for team in teamListACC: teamList.append(team)
      for team in teamListBigTen: teamList.append(team)
      for team in teamListBigTwelve: teamList.append(team)
      for team in teamListPACTwelve: teamList.append(team)
      for team in teamListSEC: teamList.append(team)
      teamList.append('notre-dame')

if verbose > 1:
      iteam=0
      for team in teamList:
            print " loading team ",teamList[iteam]
            iteam+=1

if reloadData:
      for team in teamList:
            if verbose:
                  print "team: ",team
            soup = BeautifulSoup(urllib2.urlopen("https://www.sports-reference.com/cfb/schools/{school}/{year}/gamelog/".format(school=team, year=year)).read(),'lxml')
            parsed = soup.find_all("td")
            passTotal = int(parsed[len(parsed)-18].string)
            rushTotal = int(parsed[len(parsed)-15].string)
            firstDowns = int(parsed[len(parsed)-6].string)
            penalties = int(parsed[len(parsed)-4].string)
            turnTotal = int(parsed[len(parsed)-1].string)
            
            record = unicode(soup.find_all("p")[2])
            pattern=re.compile("\d{1,2}")
            wins = int(pattern.findall(record)[0])
            losses = int(pattern.findall(record)[1])
            winPct = float(wins)/float(wins+losses)
            if verbose:
                  print "wins: ",wins, " losses: ",losses, " win pct: ",winPct
            win_pct.update({team: winPct})
            
            #the defensive stats are protected in a comment
            comments = BeautifulSoup(soup.find_all(string=lambda text:isinstance(text,Comment))[17].string,"lxml")
            parsed = comments.find_all("td")
            defTotal = int(parsed[len(parsed)-18].string) + int(parsed[len(parsed)-15].string)
            turnTotal = int(parsed[len(parsed)-1].string) - turnTotal
            teams.update({team : [passTotal, rushTotal, firstDowns, penalties, defTotal, turnTotal]})
            if saveFiles:
                  file = open('{year}/{school}.txt'.format(year=year, school=team),'w')
                  fileContent = [passTotal,rushTotal,firstDowns,penalties,defTotal,turnTotal,winPct]
                  json.dump(fileContent,file)
            if verbose:    
                  print " passTotal: ",passTotal, " rushTotal: ", rushTotal, " defTotal: ", defTotal, " turnTotal: ", turnTotal
	      
else:
      for team in teamList:
            file = open('{year}/{school}.txt'.format(year=year, school=team),'r')
            fileContent = json.load(file)
            #teamData = [fileContent[i] for i in range(0,6)]
            teamData = [fileContent[0], fileContent[1], fileContent[4], fileContent[5]]
            win_pct.update({team: fileContent[6]})
            teams.update({team : teamData})
            if verbose:
                  print "team: ",team, " passTotal: ",teamData[0], " rushTotal: ", teamData[1], " defTotal: ", teamData[2], " turnTotal: ", teamData[3]
                  print "win pct: ",fileContent[len(teamData)]

#transform dict to 2D array
teamArr = []
winPctArr = []
for team in teams:
	teamArr.append(teams[team])
	winPctArr.append(win_pct[team])

#heavy lifting done here
#clf = Ridge(alpha=1.0, normalize="True")
clf = SGDRegressor(loss="squared_loss", penalty="l2")
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(teamArr)
clf.fit(X=scaler.transform(teamArr), y=winPctArr)

predictPct = clf.predict(scaler.transform(teamArr))
#iteam=0
#for team in teams:
#      print teamArr[iteam], " ", winPctArr[iteam], " ",predictPct[iteam]
#      iteam+=1

#sort by predictive strength
iteam=0
sortedTeamDict = {}
for team in teams:
      sortedTeamDict.update({team : predictPct[iteam]})
      iteam+=1
sortedTeams = sorted(sortedTeamDict, key=lambda key: sortedTeamDict[key], reverse=True)

#print out
iteam=0
for team in teams:
      print iteam+1, " ", sortedTeams[iteam], " (", '{0:.4f}'.format(sortedTeamDict[sortedTeams[iteam]]),")"
      iteam+=1

#spit out debug predictive behavior
print "Ole Miss: ", sortedTeamDict['mississippi'], " TCU: ", sortedTeamDict['texas-christian'], " Penn St: ", sortedTeamDict['penn-state'], '\n'
#print "Hypothetical: ",predictPct[3]


