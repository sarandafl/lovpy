import re
import os
import time
import requests
from argparse import ArgumentParser
from geopy.geocoders import GoogleV3
from clint.textui import colored, puts


def get_username(json):
    """
    Get Lovoo username from JSON response.
    :param json: JSON response
    :return: Lovoo username as string
    """
    try:
        return json['name']
    except KeyError:
        return None


def get_freetext(json):
    """
    Get status text from JSON response.
    :param json: JSON response
    :return: User status as string
    """
    try:
        return json['freetext']
    except KeyError:
        return None


def get_whazzup(json):
    """
    Get status text from JSON response.
    :param json: JSON response
    :return: User status as string
    """
    try:
        return json['whazzup']
    except KeyError:
        return None


def get_hometown(json):
    """
    Get user hometown from JSON response
    :param json: JSON response
    :return: User hometown as string
    """
    try:
        return json['locations']['home']['city']
    except KeyError:
        return None


def get_country(json):
    """
    Get user country from JSON response
    :param json: JSON response
    :return: User country as string
    """
    try:
        return json['locations']['home']['country']
    except KeyError:
        return None


def get_age(json):
    """
    Get user age from JSON response
    :param json: JSON response
    :return: User age as integer
    """
    try:
        return int(json['age'])
    except KeyError:
        return None


def extract_snap(text):
    """
    Extract Snapchat username from text.
    Matches sc, snap, snapchat, ghost emoji regardless of case.
    :param text: Text containing possible Snapchat username
    :return: Snapchat username as string
    """
    regex = r'(?:(?:👻\W*)?(?:(?:(?:snap(?:chat)?\b)(?:.me)?)|(?:sc\b))|(?:👻))(?:\W)*(?P<username>(?:[a-z][\w\.-]{1,13}[a-z0-9])\b)(?:.?👻)?'
    pattern = re.compile(regex, re.IGNORECASE)
    try:
        return re.search(pattern, str(text)).group('username')
    except AttributeError:
        return None


def snapcode_exists(path):
    """
    Check if Snapcode has already been downloaded.
    :param username: The name of the Snapcode to check
    :return: boolean
    """
    if os.path.exists(path + '.svg'):
        log(msg='SnapCode already saved...', mode='e')
        return True


def check_api(username, format, size):
    headers = {
        'User-Agent': 'Snapchat/8.0.1.3 (Nexus 5; Android 21; gzip)',
        'Accept-Language': 'en-GB;q=1, en;q=0.9',
        'Accept-Locale': 'en',
        'Access-Control-Allow-Origin': '*'
    }
    api_endpoints = [
        'https://feelinsonice-hrd.appspot.com/web/deeplink/snapcode?username=' + username + '&type=' + format + '&size=' + size + '',
        'https://feelinsonice.appspot.com/web/deeplink/snapcode?username=' + username + '&type=' + format + '&size=' + size + ''
    ]

    for endpoint in api_endpoints:
        r = requests.get(endpoint, headers=headers)
        if len(r.text) == 0:
            log(msg='Unable to retrive SnapCode from: ' + endpoint, mode='e')
        else:
            return r
    return None


def get_snapcode(username, path, size='400', format='SVG'):
    """
    Fetch the Snapcode of the given user via unofficial Snapchat API.
    :param username: Username to get Snapcode for
    :param size: Snapcode size
    :param format: Snapcode format as SVG, JPG, PNG
    :return: Snapcode as defined by :param format
    """
    if not snapcode_exists(os.path.join(path, username)):
        api_response = check_api(username=username, format=format, size=size)
        if api_response:
            log(msg='Saving ' + username + '.svg...')
            with open(path + '/' + username + '.svg', 'wb') as snapcode:
                for chunk in api_response.iter_content(chunk_size=1024):
                    if chunk:
                        snapcode.write(chunk)
            return True
        log(msg='Script exiting - API timeout...', mode='e')
        exit()


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_coordinates(location):
    geolocator = GoogleV3()
    target = geolocator.geocode(location)
    return {'lat': str(target.latitude), 'long': str(target.longitude)}


def get_args():
    parser = ArgumentParser()
    parser.add_argument("-u", dest="username", help="Lovoo username")
    parser.add_argument("-p", dest="password", help="Lovoo password")
    parser.add_argument("-l", dest="location", help="Location to scan")
    parser.add_argument("-r", dest="range", help="Searchradius from start location")
    parser.add_argument("-f", dest="format", help="Format of saved SnapCode")
    parser.add_argument("--min-age", dest="min_age", help="Minimum user age")
    parser.add_argument("--max-age", dest="max_age", help="Maximum user age")
    parser.add_argument("--page", dest="page", help="Start page")
    args = parser.parse_args()
    return args


def log(msg, mode='s'):
    log_date = '[' + time.strftime("%d.%m_%H:%M:%S") + ']'
    if mode == 'e':
        log_output = colored.white(log_date) + colored.red('[ERROR]' + msg)
    elif mode == 'i':
        log_output = colored.white(log_date) + colored.yellow('[INFO]' + msg)
    elif mode == 'c':
        log_output = colored.white(log_date) + colored.white('[COMMENT]' + msg)
    elif mode == 'd':
        log_output = colored.white(log_date) + colored.white('[COMMENT]' + msg)
    else:
        log_output = colored.white(log_date) + colored.green(msg)
    puts(log_output)


def main():
    args = get_args()
    coordinates = get_coordinates(args.location)

    log(msg='Searching: ' + args.location, mode='i')

    _PAGENUM = int(args.page)
    _LAT = coordinates['lat']
    _LONG = coordinates['long']

    payload = {
        '_username': args.username,
        '_password': args.password,
        '_remember_me': 'false'
    }

    with requests.Session() as session:
        login = session.post('https://www.lovoo.com/login_check', data=payload)
        log(msg='Login status:' + login.reason, mode='i')

        while True:
            members = session.get('https://www.lovoo.com/api_web.php/users?ageFrom=' + args.min_age + '&ageTo=' + args.max_age + '&gender=2&genderLooking=1&isOnline=true&latitude=' + _LAT + '&longitude=' + _LONG + '&orderBy=distance&radiusTo=' + args.range + '&resultPage=' + str(_PAGENUM) + '&type=env&userQuality%5B0%5D=pic')
            users = members.json()

            if len(users['response']['result']) == 0:
                log(msg='No more memebers!', mode='e')
                exit()

            for user in users['response']['result']:
                userinfo = {
                    'username': get_username(user),
                    'age': get_age(user),
                    'hometown': get_hometown(user),
                    'country': get_country(user),
                    'freetext': get_freetext(user),
                    'whazzup': get_whazzup(user)
                }

                sc_freetext = extract_snap(get_freetext(userinfo))
                sc_whazzup = extract_snap(get_whazzup(userinfo))

                savepath = os.path.join('snapcodes', userinfo['country'], userinfo['hometown'])

                if sc_freetext:
                    log(msg='Found ' + sc_freetext + '!', mode='c')
                    get_snapcode(username=sc_freetext, path=mkdir(path=savepath))
                elif sc_whazzup:
                    log(msg='Found ' + sc_whazzup + '!', mode='c')
                    get_snapcode(username=sc_whazzup, path=mkdir(path=savepath))
                else:
                    continue

                time.sleep(2)
            _PAGENUM += 1
            log(msg='Moving to page ' + str(_PAGENUM), mode='i')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log(msg='Lovpy exiting...', mode='e')
