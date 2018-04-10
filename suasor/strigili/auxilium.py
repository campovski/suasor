import os

# URLs
URL_BASE = 'https://www.facebook.com/'
URL_POST_LOGIN = 'https://www.facebook.com/login.php?login_attempt=1&lwv=111'

# A set of all people we have found among friends of friends. We create a set so that every
# person will be checked only once.
PEOPLE_DISCOVERED = set()

# A dictionary of people data we managed to scrap.
PERSON_DATA = {}

"""
	Sets up directory structure if it does not exist yet.
	Must be called at the very beginning of execution of __main__.
"""
def setup_directories():
	created = False
	if not os.path.isdir(DIR_DATA):
		os.mkdir(DIR_DATA)
		created = True
	if not os.path.isdir(DIR_DATA_DEBUG):
		os.mkdir(DIR_DATA_DEBUG)
		created = True
	if not os.path.isdir(DIR_DATA_PEOPLE):
		os.mkdir(DIR_DATA_PEOPLE)
		created = True
	if not os.path.isdir(DIR_DATA_IMAGES):
		os.mkdir(DIR_DATA_IMAGES)
		created = True
	if not os.path.isdir(DIR_DATA_LOG):
		os.mkdir(DIR_DATA_LOG)
		created = True
	return created

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
	pattern = re.compile(r'<a class=".*?" accesskey="2" data-gt=".*?" href="https://www.facebook.com/(?P<your_id>.*?)" title=')
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

	regex = '<div class="fsl fwb fcb".*?<a href="' + URL_BASE + '(?P<friends_id>.*?)\\?'
	pattern = re.compile(r'{}'.format(regex))
	for match in re.findall(pattern, friends_page.text.encode('utf8')):
		if match != 'profile.php':
			PEOPLE_DISCOVERED.add(match)
			PERSON_DATA[user_id]['friends'].append(match)

"""
	The core of scraping. It scraps all data about a person it can; profile picture,
	name, date of birth, city of residence, school, relationship status, city of origin.
	It saves the data to a file and dictionary PERSON_DATA.
	TODO More ideas of what to scrap.
	@param session: Current session
	@param user_id: Scraping data for this user
"""
def strigili_princeps(session, user_id):
	# Patterns used in regex searches to extract data.
	pattern_name = re.compile(r'href="{0}{1}">(?P<name>.*?)</a>'.format(URL_BASE, user_id))
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
	if _rescrap_known_data or user_data is None:
		PERSON_DATA[user_id] = {
			'name': None,
			'picture_url': None,
			'birthday': None,
			'study': None,
			'lives_in': None,
			'from': None,
			'relationship': None,
			'friends': []
		}

		# Get about page which is located at URL_BASE/user_id/about.
		r = s.get(URL_BASE + user_id + '/about')
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
			_log('WARNING', 'strigili', 'strigili_princeps', 'Couldn\'t extract name for user {}'.format(user_id))

		# Search for picture which should always be present.
		result = re.search(pattern_picture_url, html_code)
		if result:
			PERSON_DATA[user_id]['picture_url'] = result.group('picture_url').replace('&amp;', '&')
		else:
			_log('WARNING', 'strigili', 'strigili_princeps', 'Couldn\'t extract picture url for user {}'.format(user_id))

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
			'friends': list(Friendship.objects.filter(user1=user_id).values_list('user2', flat=True))
		}

		# Add user_id to PEOPLE_DISCOVERED.
		PEOPLE_DISCOVERED.add(user_id)

		# Update PEOPLE_DISCOVERED with friends read from file. If we do not do this,
		# we cannot loop through their friends, potentially resulting in program not
		# working if do not reload data.
		PEOPLE_DISCOVERED.update(PERSON_DATA[user_id]['friends'])

"""
	Gets all profile pictures and saves them to DIR_DATA_IMAGES as <user_id>.jpg.
"""
def get_profile_pictures():
	number_of_people = len(PERSON_DATA)
	for i, user_id in enumerate(PERSON_DATA):
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
			else:
				suasor.auxilium._log('WARNING', 'strigili', 'get_profile_pictures', \
					'Couldn\'t load image for user {}'.format(user_id))


"""
	Main function, called from view.
	@param username: Facebook user
	@return None if wrong credentials, False if failed to create dirs, else number of scrapped people
"""
def strigili(username, password, depth, roots, rescrap):
	import requests
	import re
	import sys
	import json
	import datetime
	from suasor.settings import DEBUG, DIR_DATA_DEBUG, DIR_DATA_IMAGES, DIR_DATA_PEOPLE
	from suasor.models import Friendship, UserData
	import suasor.auxilium

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
		'prefill_contact_point': EMAIL,
		'prefill_source': 'browser_dropdown',
		'prefill_type': 'password',
		'skstamp': 'eyJyb3VuZHMiOjUsInNlZWQiOiI2ZDAxZDcwZjIwZjkyNWU1OTA2ZDY2ZWUwOTQ2ODM4YyIsInNlZWQyIjoiNjllYTg2MjhkODMyMGUyNmIxNDNhOTkwNjFmMmY4ZDgiLCJoYXNoIjoiM2I4OWZlMTk5OGJmNjEwYzllNjI1ZjNkMTQ4YzhjOTIiLCJoYXNoMiI6IjBjMjU4ZjU5NmI5NGYyNGU0MDMwZGQ1MWZiMDJiODlhIiwidGltZV90YWtlbiI6ODQ4MDAsInN1cmZhY2UiOiJsb2dpbiJ9'
	}

	# Get custom search roots
	if roots:
		_custom_search_roots = roots.split(',')

	# Setup directories.
	try:
		setup_directories()
	except:
		return False

	# Everything has to be done in one session so we do not lose login.
	with requests.session() as s:
		# Get session cookie.
		s.get(URL_BASE)

		# Login.
		r = s.post(URL_POST_LOGIN, LOGIN_FORM_DATA)

		if not is_valid_login(r.text):
			return None

		# Save the page to file for debugging purposes.
		if DEBUG:
			with open(os.path.join(DIR_DATA_DEBUG, '_facebook.html'), 'w') as f:
				f.write(r.text.encode('utf8'))
			_log('DEBUG', 'strigili', 'strigili', 'Main Facebook page saved to: ' + str(os.path.join(DIR_DATA_DEBUG, '_facebook.html')))

		# Add your ID to PEOPLE_DISCOVERED as a starting point for search if no custom search
		# roots have been specified.
		if _custom_search_roots:
			PEOPLE_DISCOVERED.update(_custom_search_roots)
		else:
			my_id = get_your_id(r.text.encode('utf8'))
			PEOPLE_DISCOVERED.add(my_id)

		# Get friends to desired depth. Depth + 1 because on depth 0 is the head, that is you.
		number_of_people_through_sp = 0
		for i in range(depth+1):
			# Get profile pages of every person we discovered and extract the data
			# we can get (profile pic, name, date of birth, city, institutes, etc.).
			# Search only through people that are not you to save some time because I
			# guess you are not searching for yourself or your dummy profile.
			for user_id in [uid for uid in PEOPLE_DISCOVERED if uid not in PERSON_DATA]:
				strigili_princeps(s, user_id)
				number_of_people_through_sp += 1

		# Now that we hopefully have all data extracted, we can get the profile pictures.
		# Maybe it is better to get profile pictures as we search for people and at the same time
		# run analysis in separate thread so that we can stop scraping data if we already find a match.
		# For now, we will scrap all data first, then get profile pictures and at the end return the top
		# matches, so not only the best match, but potential matches.
		get_profile_pictures()

		return number_of_people_through_sp
