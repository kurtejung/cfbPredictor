
##http://scikit-learn.org/stable/modules/sgd.html

from sklearn.linear_model import Ridge, SGDRegressor
from sklearn import ensemble
import urllib2, re, json, difflib
from bs4 import BeautifulSoup
from bs4 import Comment
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

#### Global Parameters ###

reloadData = False
saveFiles = True
year = 2017
teamList = []

doTest = False
doPower5 = False
doAll = True

verbose = 1

writeCSV = True

doPlotting = True
isGradientBoosted = False

###########################

teams = {}
win_pct = {}
opp_win_pct = {}

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

defunctList = {'alabama-birmingham':2016, 'coastal-carolina':2016}

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
      
if doTest:
      teamList.append('notre-dame')

if verbose > 1:
      iteam=0
      for team in teamList:
            print " loading team ",teamList[iteam]
            iteam+=1

if reloadData:
      
      #now get the opponent win percentage from another site
      if(year==2017):
            soup2 = BeautifulSoup(urllib2.urlopen("http://www.cpiratings.com/archives/{year}w15_table.html".format(year=year)).read(),'lxml')
      else:
            soup2 = BeautifulSoup(urllib2.urlopen("http://www.cpiratings.com/archives/{year}post_table.html".format(year=year)).read(),'lxml')
      teamTable = soup2.find_all('table')[0]
            
      rows = teamTable.find_all('tr')
      for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols[1] = re.sub("[\(\[].*?[\)\]]","",cols[1]).strip()
            teamArg = cols[1].lower().replace(" ", "-")
            if(teamArg=="team"):
                  continue
            if(teamArg=="smu"):
                  teamArg="southern-methodist"
            if(teamArg=="lsu"):
                  teamArg="louisiana-state"
            if(teamArg=="utep"):
                  teamArg="texas-el-paso"
            if(teamArg=="texas-st-san-marcos"):
                  teamArg="texas-state"
            if(teamArg=="unlv"):
                  teamArg="nevada-las-vegas"
            if(teamArg=="tcu"):
                  teamArg="texas-christian"
            #print teamArg
            teamClose = difflib.get_close_matches(teamArg,teamList,1,0.7)
            if(len(teamClose)==0):
                  print "cannot find any team matches for ",teamArg,"!"
                  continue
            teamClosest=teamClose[0]
            opp_win_pct.update({teamClosest: cols[13]})
            #print "opp win pct for ", teamClosest, "( ",teamArg," ) is ", cols[13]
      
      
      for team in teamList:
            if(team in defunctList):
                  if(defunctList[team]==year):
                        continue
            if verbose:
                  print "team: ",team
            soup = BeautifulSoup(urllib2.urlopen("https://www.sports-reference.com/cfb/schools/{school}/{year}/gamelog/".format(school=team, year=year)).read(),'lxml')
            parsed = soup.find_all("td")
            passTotal = int(parsed[len(parsed)-18].string)
            rushTotal = int(parsed[len(parsed)-15].string)
            firstDowns = int(parsed[len(parsed)-6].string)
            penalties = int(parsed[len(parsed)-4].string)
            turnTotal = int(parsed[len(parsed)-1].string)
            totalGameString = parsed[len(parsed)-25].string
            totalGames=int(re.split("(^\d+)",totalGameString)[1])
            
            record = unicode(soup.find_all("p")[2])
            pattern=re.compile("\d{1,2}")
            wins = int(pattern.findall(record)[0])
            losses = int(pattern.findall(record)[1])
            winPct = float(wins)/float(wins+losses)
            if verbose:
                  print "wins: ",wins, " losses: ",losses, " win pct: ",winPct
            win_pct.update({team: winPct})
            
            #the defensive stats are protected in a comment
            comments = BeautifulSoup(soup.find_all(string=lambda text:isinstance(text,Comment))[18].string,"lxml")
            parsed = comments.find_all("td")
            defTotal = int(parsed[len(parsed)-18].string) + int(parsed[len(parsed)-15].string)
            turnTotal = int(parsed[len(parsed)-1].string) - turnTotal
            
            teamInfo = [passTotal, rushTotal, firstDowns, penalties, defTotal, turnTotal]
            #for item in range(0,len(teamInfo)):
                  #teamInfo[item] = float(teamInfo[item])/float(totalGames)
            teams.update({team : teamInfo})
            
            if saveFiles:
                  file = open('{year}/{school}.txt'.format(year=year, school=team),'w')
                  fileContent = teamInfo
                  fileContent.append(winPct)
                  fileContent.append(opp_win_pct[team])
                  #fileContent = [passTotal,rushTotal,firstDowns,penalties,defTotal,turnTotal,winPct,opp_win_pct[team]]
                  json.dump(fileContent,file)
            if verbose:
                  print "games played: ",totalGames
                  print " passTotal: ",teamInfo[0], " rushTotal: ", teamInfo[1], " defTotal: ", teamInfo[4], " turnTotal: ", teamInfo[5], " opp win pct: ",opp_win_pct[team]
	      
for team in teamList:
      if(team in defunctList):
            if(defunctList[team]==year):
                  continue
      file = open('{year}/{school}.txt'.format(year=year, school=team),'r')
      fileContent = json.load(file)
      teamData = [fileContent[i] for i in range(0,6)]
      #teamData = [fileContent[0], fileContent[1], fileContent[4], fileContent[5]]
      win_pct.update({team: fileContent[6]})
      opp_win_pct.update({team: fileContent[7]})
      for i in [0,1,2,5]:
            teamData[i]*=(float(fileContent[7])**0.3)
      teamData[4]/=(float(fileContent[7])**0.1)
      teams.update({team : teamData})
      if verbose:
            print "team: ",team, " passTotal: ",teamData[0], " rushTotal: ", teamData[1], " defTotal: ", teamData[4], " turnTotal: ", teamData[5]
            print "win pct: ",fileContent[6], " opp win pct: ",fileContent[7]

#transform dict to 2D array
teamArr = []
winPctArr = []
oppWinPctArr = []
input_names = ['passTotal','rushTotal','firstDowns','penalties','defTotal','turnTotal','oppWinPct']

#key here is to scale the winning percentage by the opponent's winning pct
for team in teams:
      teamArr.append(teams[team])
      adjustedWinPct = float(win_pct[team])
      winPctArr.append(adjustedWinPct)
      oppWinPctArr.append(opp_win_pct[team])

#heavy lifting done here

#do a simple ridge regression
clf = Ridge(alpha=1.0, normalize="True")

#do a stochastic gradient descent
#clf = SGDRegressor(loss="squared_loss", penalty="l2", tol=None, max_iter=5)

#do a gradient boosted tree
params = {'n_estimators':50, 'max_depth':5, 'min_samples_split':5, 'learning_rate':0.05, 'loss':'ls'}
if isGradientBoosted:
      clf = ensemble.GradientBoostingRegressor(**params)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(teamArr)
clf.fit(X=scaler.transform(teamArr), y=winPctArr)

#predictPct = clf.predict(scaler.transform(teamArr))
predictPct = clf.predict(scaler.transform(teamArr))

from sklearn.model_selection import cross_val_score
#from sklearn.model_selection import train_test_split
model_scores = cross_val_score(clf, scaler.transform(teamArr), winPctArr, cv=5, verbose=0)
print model_scores
print "Accuracy: %0.2f (+/- %0.2f)" % (model_scores.mean(),model_scores.std())

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

#pyplot
if doPlotting:
      
      def func(x, a, b):
            return (a * x) + b
      np_winpctArr = np.array(winPctArr)
      np_predictPct = np.array(predictPct)
      popt, pcov = curve_fit(func,np_winpctArr,np_predictPct)
      
      plt.figure(figsize=(12,6))
      plt.subplot(1,2,1)
      plt.scatter(winPctArr,predictPct)
      plt.plot(np_winpctArr, func(np_winpctArr, *popt), 'g--', label='linear fit')
      plt.xlabel("Actual Win Pct")
      plt.ylabel("Predicted Win Pct")
      
      if isGradientBoosted:
            feature_importance = clf.feature_importances_
            # make importances relative to max importance
            feature_importance = 100.0 * (feature_importance / feature_importance.max())
            sorted_idx = np.argsort(feature_importance)
            pos = np.arange(sorted_idx.shape[0]) + .5
            plt.subplot(1, 2, 2)
            plt.barh(pos, feature_importance[sorted_idx], align='center')
            print sorted_idx
            feature_names = [x for _,x in sorted(zip(sorted_idx,input_names))]
            plt.yticks(pos, feature_names)
            plt.xlabel('Relative Importance')
            plt.title('Variable Importance')
      
      plt.show()
      
      
      
      

#print out
iteam=0
for team in teams:
      print iteam+1, " ", sortedTeams[iteam], " (", '{0:.4f}'.format(sortedTeamDict[sortedTeams[iteam]]),")"
      iteam+=1

if(writeCSV):
      iteam=0
      fout = open('ranking_{year}.csv'.format(year=year),'w')
      fout.write("RANKING, TEAM, MVA SCORE\n")
      for team in teams:
            writeString = str(iteam+1)+", "+str(sortedTeams[iteam])+", "+'{0:.4f}'.format(sortedTeamDict[sortedTeams[iteam]])+'\n'
            fout.write(writeString)
            iteam+=1
      
      
#spit out debug predictive behavior
#print "Ole Miss: ", sortedTeamDict['mississippi'], " TCU: ", sortedTeamDict['texas-christian'], " Penn St: ", sortedTeamDict['penn-state'], '\n'
#print "Hypothetical: ",predictPct[3]


