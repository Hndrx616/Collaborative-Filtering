# Template Name: reccomendations.py
# Author: Stephen Hilliard (c) 2013
# Developer: Stephen Hilliard (c) 2013
# license http://www.gnu.org/licenses/gpl-3.0.html GPL v3 or later
# @project: reccomendations

# Nested dictionary of business review critics and their ratings based on site usage
critics={'User 1': {'Google Review':2.5, 'Twitter': 3.5, 'Yelp': 3.0, 'Amazon Customer Review': 3.5, 'Yahoo Local': 2.5, 'Facebook Rating': 3.0},'User 2': {'Google Review':3.0, 'Twitter': 3.5, 'Yelp': 1.5, 'Amazon Customer Review': 5.0, 'Yahoo Local': 3.5, 'Facebook Rating': 3.0},'User 3': {'Google Review':2.5, 'Twitter': 3.0, 'Amazon Customer Review': 3.5, 'Facebook Rating': 4.0},'User 4': {'Twitter': 3.5, 'Yelp': 3.0, 'Amazon Customer Review': 4.0, 'Yahoo Local': 2.5, 'Facebook Rating': 4.5},'User 5': {'Google Review':3.0, 'Twitter': 4.0, 'Yelp': 2.0, 'Amazon Customer Review': 3.0, 'Yahoo Local': 2.0, 'Facebook Rating': 3.0},'User 6': {'Google Review':3.0, 'Twitter': 4.0, 'Amazon Customer Review': 5.0, 'Yahoo Local': 3.5, 'Facebook Rating': 3.0},'User 7': {'Twitter': 4.5, 'Amazon Customer Review': 4.0, 'Yahoo Local': 1.0}}

from math import sqrt
 
# Returns a distance based similarity score for person1 and person2
def sim_distance(prefs,person1,person2):
  # Get the list of shared_items
  si={}
  for item in prefs[person1]:
  	if item in prefs[person2]:
  		si[item]=1
  
  # if they have no raings in common, return 0
  if len(si)==0: return 0

  # Add up the squares of all the differences
  sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)for item in si])

  return 1/(1+sqrt(sum_of_squares))

# Returns the Pearson Correlation Coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
  # Get the list of mutually rated items
  si={}
  for item in prefs[p1]:
  	if item in prefs[p2]: si[item]=1
	
  # Find the number of elements
  n=len(si)
  
  # If they have no ratings in common, return 0
  if n==0: return 0
  
  # Add up all the preferences
  sum1=sum([prefs[p1][it] for it in si])
  sum2=sum([prefs[p2][it] for it in si])
  
  # Sum up the squares
  sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
  sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
  
  # Sum up the products
  pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
  
  # Calculate Pearson score
  num=pSum-(sum1*sum2/n)
  den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
  if den==0: return 0
  
  r=num/den
  
  return r

# Returns the best matches for person from the prefs dictionary
# Number of results and similarity function are optional parameters
def topMatches(prefs,person,n=5,similarity=sim_pearson):
	scores=[(similarity(prefs,person,other),other)for other in prefs if other!=person]

	# Sort the list so the highest scores appear at the top
	scores.sort()
	scores.reverse()
	return scores[0:n]

# Get reccommendations for a person by using a weighted avg of every other ranking
def getRecommendations(prefs,person,similarity=sim_pearson):
	totals={}
	simSums={}
	for other in prefs:
		# don't compare me to myself
		if other==person: continue
		sim=similarity(prefs,person,other)

		# ignore scores of zero or lower
		if sim<=0: continue
		for iterm in prefs[other]:

			# only score reviews I haven't seen yet
			if item not in prefs[person] or prefs[person][item]==0:
				# Similarity * score
				totals.setdefault(item,0)
				totals[item]+=prefs[other][item]*sim
				# Sum of similarities
				simSums.setdefault(item,0)
				simSums[item]+=sim

	# Create a normalized list
	rankings=[(total/simSums[item],item) for item,total in totals.items()]

	# Return the sorted list
	rankings.sort()
	rankings.reverse()
	return rankings

def transformPrefs(prefs):
  result={}
  for person in prefs:
    for item in prefs[person]:
      result.setdefault(item,{})

      # Flip item and person
      result[item][person]=prefs[person][item]
  return result

def calculateSimilarItems(prefs,n=10):
  # Create a dictionay of items showing other items they
  # are most similar to.
  result={}

  # Invert the preference matrix to be item-centric
  itemPrefs=transformPrefs(prefs)
  c=0
  for item in itemPrefs:
    # Status updates for large datasets
    c+=1
    if c%100==0: print "%d / %d" % (c,len(itemPrefs))
    # Find the most similar items to this one
    scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
    result[item]=scores
  return result

def getRecommendedItems(prefs,itemMatch,user):
  userRatings=prefs[user]
  scores={}
  totalSim={}

  # Loop over items rated by this user
  for (item,rating) in userRatings.items():

    # Loop over items similar to this one
    for (similarity,item2) in itemMatch[item]:

      # Ignore if this user has already rated this item
      if item2 in userRatings: continue

      # Weighted sum of rating times similarity
      scores.setdefault(item2,0)
      scores[item2]+=similarity*rating

      # Sum of all the similarities
      totalSim.setdefault(item2,0)
      totalSim[item2]+=similarity

    # Divide each total score by total weighting to get an average
    rankings=[(score/totalSim[item],item) for item,score in scores.items()]

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

def loadReviewLens(path='/data/reviewlens'):

  # Get review titles
  reviews={}
  for line in open(path+'/u.item'):
    (id,title)=line.split('|')[0:2]
    reviews[id]=title

    # Load data
    prefs={}
    for line in open(path+'u/data'):
      (user,reviewid,rating,ts)=line.split('\t')
      prefs.setdefault(user,{})
      prefs[user][reviews[reviewid]]=float(rating)
    return prefs