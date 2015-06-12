from datetime import datetime
import httplib
import json
import sys
import urllib2

config_file = sys.argv[1]
config_data = json.load(open(config_file))

# Extract data from the config file
auth_token = config_data['auth_token']
goal = config_data['goal']
username = config_data['username']

def parse_goal_file(goal_data, default_rate):
    daily_rates = [default_rate] * 7
    if 'daily_rates' in goal_data and len(goal_data['daily_rates']) == 7:
        daily_rates = goal_data['daily_rates']
    if 'weekdays' in goal_data:
        daily_rates = [goal_data['weekdays']]*5 + daily_rates[5:]
    if 'weekends' in goal_data:
        daily_rates = daily_rates[:5] + [goal_data['weekends']]*2
    for i, day in enumerate(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']):
        daily_rates[i] = goal_data.get(day, daily_rates[i])
    return daily_rates

goal_data = json.loads(urllib2.urlopen('https://www.beeminder.com//api/v1/users/%s/goals/%s.json?datapoints=true&auth_token=%s' % (username, goal, auth_token)).read())

# Length of a day
DAY = 24*60*60

# The fist date that we're going to change
start_date = goal_data['curday']+8*DAY
# Strip all items from the road after start_date (since we're changing all of them).
road_unchangeable = [road_item for road_item in goal_data['roadall'] if road_item[0] < start_date]

N_DAYS = 30

# All the rates in the config file are daily rates, but the rates of the yellow brick road might be something else.
def convert_daily_rate(rate, unit):
    """From daily rate to yellow brick road rate."""
    if unit == 'h':
        return rate / 24.0
    if unit == 'd':
        return rate
    if unit == 'w':
        return rate * 7.0
    if unit == 'm':
        return rate * 30.0
    if unit == 'y':
        return rate * 365.0

def convert_to_daily_rate(rate, unit):
    """From yellow brick road rate to daily rate."""
    if unit == 'h':
        return rate * 24.0
    if unit == 'd':
        return rate
    if unit == 'w':
        return rate / 7.0
    if unit == 'm':
        return rate / 30.0
    if unit == 'y':
        return rate / 365.0

rate_of_day = parse_goal_file(config_data, convert_to_daily_rate(goal_data['rate'], goal_data['runits']))
# Add road items with the proper dates
for i in xrange(0, N_DAYS):
    cur_date = start_date + i*DAY
    weekday = datetime.fromtimestamp(cur_date).weekday()
    cur_rate = rate_of_day[weekday]
    # Maybe there's a specific override for that day. Get it.
    cur_rate = config_data.get('day_overrides', {}).get(datetime.fromtimestamp(cur_date).date().isoformat(), cur_rate)
    road_unchangeable.append([cur_date, None, convert_daily_rate(cur_rate, goal_data['runits'])])

data = json.dumps({'roadall': json.dumps(road_unchangeable)})
url = 'https://www.beeminder.com/api/v1/users/%s/goals/%s.json?auth_token=%s' % (username, goal, auth_token)
request = urllib2.Request(url, data=data, headers={'Content-type': 'application/json'})
request.get_method = lambda: 'PUT'
httplib.HTTPConnection.debuglevel = 1
# This crazy thing is here because urllib2 is terrible at handling PUT requests, so we need a special handler...
class PutRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Return a Request or None in response to a redirect.
        This is called by the http_error_30x methods when a
        redirection response is received.  If a redirection should
        take place, return a new Request to allow http_error_30x to
        perform the redirect.  Otherwise, raise HTTPError if no-one
        else should try to handle this url.  Return None if you can't
        but another Handler might.
        """
        # This is a modified version of the parent implementation that also handles PUT and DELETE
        m = req.get_method()
        if (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m in ("POST", "PUT", "DELETE")):
            # Strictly (according to RFC 2616), 301 or 302 in response
            # to a POST MUST NOT cause a redirection without confirmation
            # from the user (of urllib2, in this case).  In practice,
            # essentially all clients do redirect in this case, so we
            # do the same.
            # be conciliant with URIs containing a space
            newurl = newurl.replace(' ', '%20')
            newheaders = dict((k,v) for k,v in req.headers.items()
                              if k.lower() not in ("content-length", "content-type")
                             )
            print newurl
            return urllib2.Request(newurl,
                           headers=newheaders,
                           origin_req_host=req.get_origin_req_host(),
                           unverifiable=True)
        else:
            raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)    

# Send the request with the updated road.
opener = urllib2.build_opener(PutRedirectHandler)
try:
    updated = opener.open(request)
except Exception, e:
    print e.read()


# Check that the road has indeed been updated.
goal_data = json.loads(urllib2.urlopen('https://www.beeminder.com//api/v1/users/%s/goals/%s.json?datapoints=true&auth_token=%s' % (username, goal, auth_token)).read())
assert goal_data['roadall'] == road_unchangeable
