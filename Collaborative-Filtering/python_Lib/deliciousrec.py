# Template Name: deliciousrec.py
# Author: Stephen Hilliard (c) 2013
# Developer: Stephen Hilliard (c) 2013
# license http://www.gnu.org/licenses/gpl-3.0.html GPL v3 or later
# @project: deliciousrec
from pydelicious import get_popular,get_userposts,get_urlposts

def initializeUserDict(tag,count=5):
	user_dict={}
	# get the top "count" popular posts
	for p1 in get_popular(tag=tag)[0:count]:
		# find all users who posted this
		for p2 in get_urlpost(p1['href']):
			user=p2['user']
			user_dict[user]={}
	return user_dict

import time
def fillItems(user_dict):
	all_items={}
	# Find links posted by all users
	for user in user_dict:
		for i in range(3):
			try:
				posts=get_userposts(user)
				break
			except:
				print "Failed user "+user+", retyring"
				time.sleep(4)
		for post in posts:
			url=post['href']
			user_dict[user][url]=1.0
			all_items[url]=1

	# Fill in missing items with 0
	for ratings in user_dict.values():
		for item in all_items:
			if item not in ratings:
				ratings[item]=0.0