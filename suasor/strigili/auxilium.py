import requests
import re
import sys
import json
import datetime
import os
import threading

from django.http import HttpResponse

from suasor.settings import DEBUG, DIR_DATA, DIR_DATA_DEBUG, DIR_DATA_IMAGES, DIR_DATA_PEOPLE, DIR_DATA_LOG
from suasor.models import Friendship, UserData
import suasor.auxilium

# URLs
URL_BASE = 'https://www.facebook.com/'
URL_POST_LOGIN = 'https://www.facebook.com/login.php?login_attempt=1&lwv=111'

# A set of all people we have found among friends of friends. We create a set so that every
# person will be checked only once.
PEOPLE_DISCOVERED = set()

# A dictionary of people data we managed to scrap.
PERSON_DATA = {}

"""
	Checks if login to Facebook has been successful (via searching for 'Recover Your Account'
	in response HTML).
	@param text: HTML code to be searched
	@return True if not found, else False
"""
def is_valid_login(text):
	return 'Recover Your Account' not in text

"""
	Function that extracts YOUR ID from main Facebook page.
	@param text: HTML code of main page
	@return your Facebook ID
"""
def get_your_id(text):
	pattern = re.compile(r'<a accesskey="2" data-gt=".*href="https://www.facebook.com/(?P<your_id>.*?)" title=')
	match = re.search(pattern, text)
	return match.group('your_id')

"""
	Function that gets HTML code of user's profile page.
	@param session: Current session
	@param user_id: Facebook ID of a person to get the profile page of
	@return HTML code of requested profile page
"""
def get_profile_page(session, user_id):
	r = session.get(URL_BASE + user_id)
	return r.text.encode('utf8')

"""
	Function that extracts friends of a person and adds them to PERSON_DATA[user_id]['friends'] and PEOPLE_DISCOVERED.
	@param session: Current session
	@param user_id: Facebook ID of user whose friends are to be extracted
"""
def get_friends(session, user_id):
	# Get friends page of a person.
	friends_page = session.get(URL_BASE + user_id + '/friends')

	regex = '<a class=".+?" href="' + URL_BASE + '(?P<friends_id>[a-zA-Z.0-9]+?)\\?'
	pattern = re.compile(r'{}'.format(regex))
	for match in re.findall(pattern, friends_page.text.encode('utf8')):
		if match != 'profile.php' and match != 'settings' and match != user_id:
			PEOPLE_DISCOVERED.add(match)
			PERSON_DATA[user_id]['friends'].append(match)

"""
	Gets profile picture and saves it to DIR_DATA_IMAGES as <user_id>.jpg.
	@param user_id: Facebook ID of user we want to get profile picture of
"""
def get_profile_picture(user_id):
	if PERSON_DATA[user_id]['picture_url'] is not None:
		# Extract extension of image.
		# Extension is probably always ".jpg" but still better to be robust.
		_, temp_extension = PERSON_DATA[user_id]['picture_url'].rsplit('.', 1)
		extension, _ = temp_extension.split('?', 1)

		# Get the picture.
		picture = requests.get(PERSON_DATA[user_id]['picture_url']).content

		# If picture has been found, write it to file. Otherwise log a warning.
		if picture:
			with open(os.path.join(DIR_DATA_IMAGES, '{0}.{1}'.format(user_id, extension)), 'w') as f:
				f.write(picture)
			return True
		else:
			suasor.auxilium._log('WARNING', 'strigili', 'get_profile_pictures', \
				'Couldn\'t load image for user {}'.format(user_id))
			return False
	return False

"""
	The core of scraping. It scraps all data about a person it can; profile picture,
	name, date of birth, city of residence, school, relationship status, city of origin.
	It saves the data to a file and dictionary PERSON_DATA.
	TODO More ideas of what to scrap.
	@param session: Current session
	@param user_id: Scraping data for this user
"""
def strigili_princeps(session, user_id, rescrap):
	# Patterns used in regex searches to extract data.
	pattern_name = re.compile(r'href="{0}{1}">(?P<name>.*?)<'.format(URL_BASE, user_id))
	pattern_picture_url = re.compile(r'<img class="profilePic.*?src="(?P<picture_url>.*?)"')
	pattern_birthday = re.compile(r'Birthday</span.*?<div>(?P<birthday>.*?)</div>')
	pattern_study = re.compile(r'Studie(.*?>)?(?P<study>.*?)</')
	pattern_lives_in = re.compile(r'Lives in(.*?>)?(?P<lives_in>.*?)</')
	pattern_from = re.compile(r'From .*?show=\"1\">(?P<from>.*?)</')
	# TODO pattern_relationship (with)

	# Get data on user from database or None if user is not in database.
	try:
		user_data = UserData.objects.get(user_id=user_id)
	except UserData.DoesNotExist:
		user_data = None

	# Rescrap data if requested or if data is not found in database.
	if rescrap or user_data is None:
		PERSON_DATA[user_id] = {
			'name': None,
			'picture_url': None,
			'birthday': None,
			'study': None,
			'lives_in': None,
			'from': None,
			'relationship': None,
			'friends': [],
			'has_picture': False
		}

		# Get about page which is located at URL_BASE/user_id/about.
		r = session.get(URL_BASE + user_id + '/about')
		html_code = r.text.encode('utf8')

		# Write page to file for debugging purposes.
		if DEBUG:
			with open(os.path.join(DIR_DATA_DEBUG, '{0}.html'.format(user_id)), 'w') as f:
				f.write(html_code)

		# Search for name which we extract from name over banner picture.
		result = re.search(pattern_name, html_code)
		if result:
			PERSON_DATA[user_id]['name'] = result.group('name')
		else:
			suasor.auxilium._log('WARNING', 'strigili', 'strigili_princeps', 'Couldn\'t extract name for user {}'.format(user_id))

		# Search for picture which should always be present.
		result = re.search(pattern_picture_url, html_code)
		if result:
			PERSON_DATA[user_id]['picture_url'] = result.group('picture_url').replace('&amp;', '&')
		else:
			suasor.auxilium._log('WARNING', 'strigili', 'strigili_princeps', 'Couldn\'t extract picture url for user {}'.format(user_id))

		# Search for birthday. Might return None.
		result = re.search(pattern_birthday, html_code)
		PERSON_DATA[user_id]['birthday'] = result.group('birthday') if result is not None else None

		# Search for institute where person studies. Might return None.
		result = re.search(pattern_study, html_code)
		PERSON_DATA[user_id]['study'] = result.group('study') if result is not None else None

		# Search for city a person lives in. Might return None.
		result = re.search(pattern_lives_in, html_code)
		PERSON_DATA[user_id]['lives_in'] = result.group('lives_in') if result is not None else None

		# Search for city where person is coming from. Might return None.
		result = re.search(pattern_from, html_code)
		PERSON_DATA[user_id]['from'] = result.group('from') if result is not None else None

		# Search for relationship status. Might return None.
		# TODO PERSON_DATA[user_id]['relationship'] = re.search(pattern_relationship, html_code).group('relationship')

		# Get friends of current person. The method also adds them to PERSON_DATA so they will
		# be written to database.
		get_friends(session, user_id)

		# Save profile picture of current person to disk. If successful, we need to mark it.
		PERSON_DATA[user_id]['has_picture'] = get_profile_picture(user_id)

		# Save data to database. Create new object if it has not been found.
		if not user_data:
			user_data = UserData()
		user_data.user_id = user_id
		user_data.name = PERSON_DATA[user_id]['name']
		user_data.birthday = PERSON_DATA[user_id]['birthday']
		user_data.lives_in = PERSON_DATA[user_id]['lives_in']
		user_data.comes_from = PERSON_DATA[user_id]['from']
		user_data.study = PERSON_DATA[user_id]['study']
		user_data.picture_url = PERSON_DATA[user_id]['picture_url']
		user_data.has_saved_picture = PERSON_DATA[user_id]['has_picture']
	    # TODO user_data.married = PERSON_DATA[user_id]['married']
	    # TODO user_data.in_relationship = PERSON_DATA[user_id]['relationship']
		user_data.save()

		# Save friends.
		for friend in PERSON_DATA[user_id]['friends']:
			fs = Friendship()
			fs.user1 = user_id
			fs.user2 = friend
			fs.save()

	# We managed to retrieve data from database.
	else:
		PERSON_DATA[user_id] = {
			'name': user_data.name,
			'picture_url': user_data.picture_url,
			'birthday': user_data.birthday,
			'study': user_data.study,
			'lives_in': user_data.lives_in,
			'from': user_data.comes_from,
			'relationship': None,
			'friends': list(Friendship.objects.filter(user1=user_id).values_list('user2', flat=True)),
			'has_picture': user_data.has_saved_picture
		}

		# Add user_id to PEOPLE_DISCOVERED.
		PEOPLE_DISCOVERED.add(user_id)

		# Update PEOPLE_DISCOVERED with friends read from file. If we do not do this,
		# we cannot loop through their friends, potentially resulting in program not
		# working if do not reload data.
		PEOPLE_DISCOVERED.update(PERSON_DATA[user_id]['friends'])

"""
	Main function, called from view.
	@param username: Facebook user
	@return None if wrong credentials, False if failed to create dirs, else number of scrapped people
"""
def strigili(username, password, depth, roots, rescrap):
	# Data that needs to be passed in Facebook login form. It might not all be needed
	# but better safe than sorry.
	LOGIN_FORM_DATA = {
		'lsd': 'AVoWxZto',
		'email': username,
		'pass': password,
		'timezone': -60,
		'lgndim': 'eyJ3IjoxNDQwLCJoIjo5MDAsImF3IjoxNDQwLCJhaCI6ODc0LCJjIjoyNH0=',
		'lgnrnd': '005012__T_v',
		'lgnjs': 1516870214,
		'ab_test_data': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
		'locale': 'en_US',
		'login_source': 'login_bluebar',
		'prefill_contact_point': username,
		'prefill_source': 'browser_dropdown',
		'prefill_type': 'password',
		'skstamp': 'eyJyb3VuZHMiOjUsInNlZWQiOiI2ZDAxZDcwZjIwZjkyNWU1OTA2ZDY2ZWUwOTQ2ODM4YyIsInNlZWQyIjoiNjllYTg2MjhkODMyMGUyNmIxNDNhOTkwNjFmMmY4ZDgiLCJoYXNoIjoiM2I4OWZlMTk5OGJmNjEwYzllNjI1ZjNkMTQ4YzhjOTIiLCJoYXNoMiI6IjBjMjU4ZjU5NmI5NGYyNGU0MDMwZGQ1MWZiMDJiODlhIiwidGltZV90YWtlbiI6ODQ4MDAsInN1cmZhY2UiOiJsb2dpbiJ9'
	}

	# Get custom search roots if supplied.
	_custom_search_roots = None
	if roots:
		_custom_search_roots = roots.split(',')
		if DEBUG:
			print 'SEARCH ROOTS = {}'.format(_custom_search_roots)

	# Everything has to be done in one session so we do not lose login.
	with requests.session() as s:
		# Get session cookie.
		s.get(URL_BASE)

		if DEBUG:
			print 'Loging in...'
		# Login.
		r = s.post(URL_POST_LOGIN, LOGIN_FORM_DATA)

		if not is_valid_login(r.text):
			if DEBUG:
				print 'Failed to login!'
			return HttpResponse("Login Error: Wrong Facebook credentials.")
		if DEBUG:
			print 'Login successful!'

		# Save the page to file for debugging purposes.
		if DEBUG:
			with open(os.path.join(DIR_DATA_DEBUG, '_facebook.html'), 'w') as f:
				f.write(r.text.encode('utf8'))
			suasor.auxilium._log('DEBUG', 'strigili', 'strigili', 'Main Facebook page saved to: ' + str(os.path.join(DIR_DATA_DEBUG, '_facebook.html')))

		# Add your ID to PEOPLE_DISCOVERED as a starting point for search if no custom search
		# roots have been specified.
		if _custom_search_roots:
			PEOPLE_DISCOVERED.update(_custom_search_roots)
		else:
			my_id = get_your_id(r.text.encode('utf8'))
			PEOPLE_DISCOVERED.add(my_id)

		if DEBUG:
			print 'PEOPLE_DISCOVERED = {}'.format(PEOPLE_DISCOVERED)

		# Get friends to desired depth. Depth + 1 because on depth 0 is the head, that is you.
		number_of_people_through_sp = 0
		for i in range(depth+1):
			# Get profile pages of every person we discovered and extract the data
			# we can get (profile pic, name, date of birth, city, institutes, etc.).
			for user_id in [uid for uid in PEOPLE_DISCOVERED if uid not in PERSON_DATA]:
				if DEBUG:
					print '{0} / {1} / Getting data for {2}'.format(i, number_of_people_through_sp, user_id)
				try:
					strigili_princeps(s, user_id, rescrap)
				# If exception of some sort happens, log it to database and restart strigili.
				except Exception as e:
					suasor.auxilium._log('ERROR', 'strigili', 'strigili', e.message)
					strigili(username, password, depth, roots, rescrap)
				number_of_people_through_sp += 1

		print 'FINISHED! Processed {} people.'.format(number_of_people_through_sp)
		print '\n======================================================\n'
		return HttpResponse("Strigili has processed {} people.".format(number_of_people_through_sp))

"""
    Extend threading.Thread to remember the number of processed people.
"""
class StrigiliThread(threading.Thread):
	def __init__(self, request, username, password, depth, roots, rescrap):
		self.request = request
		self.username = username
		self.password = password
		self.depth = depth
		self.roots = roots
		self.rescrap = rescrap
		self.number_of_people_through_sp = None
		super(StrigiliThread, self).__init__()

	def run(self):
		print 'StrigiliThread: STARTED!'
		self.number_of_people_through_sp = strigili(self.username, self.password, self.depth, \
			self.roots, self.rescrap)
