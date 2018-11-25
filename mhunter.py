import logging
import requests
import argparse
import numpy
from re import search, sub

parser = argparse.ArgumentParser(description="Analyses recent BOM data to determine whether it's a good time to forrage for mushrooms.")
# mandatory arguments:
parser.add_argument("gauge_url", help="The itentifier for the BOM observation gauge you want to querry. The tool will put it into this urL: http://www.bom.gov.au/products/IDQ60801/IDQ60801.GAUGE.shtml ")
# optional arguments:
parser.add_argument("-o",
                    "--output",
                    action="store",
                    help="specifies output to write the results to. If not provided, results will be written to std out")
parser.add_argument("-v",
                    "--verbose",
                    action="store_true",
                    help="adds additional information to the output.")
args = parser.parse_args()

# TODO: think about security if I expose this publically. -- Bobby Tables

logger = logging.getLogger('mhunter')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log.log')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.debug("======")

def log(func):
    """Adds debugging log information"""
    def wrapper(*args, **kwargs):
        logger.debug("calling %s" % func.__name__)
        return func(*args, **kwargs)
    return wrapper

@log
def parse_url(url):
    """removes 'shtml' and replace it with 'json'"""
    logger.debug("recieved %s" % url)
    if search('json', url):
        logger.debug("url looks like json. %s returning as is" % parse_url.__name__)
        return url
    elif search('shtml', url):
        logger.debug("url looks like shtml. subing for json...")
        return sub('shtml', 'json', url)
    else:
        raise AttributeError("This tool only takes a url to a BOM weather observations page, for example http://www.bom.gov.au/products/IDQ60801/IDQ60801.94294.shtml")


# @log
def get_rolling_average(list_of_30m_observations, hours):
    """Gets the average value in the list over the last number of hours"""
    number_observations = hours * 2  # TODO: assert that read interval is 30m
    trimmed_list = list_of_30m_observations[:number_observations]
    try:
        return numpy.mean(trimmed_list)
    except TypeError as e:
        trimmed_list = [float(l) for l in trimmed_list]
        return numpy.mean(trimmed_list)

@log
def get_std_dev(list_of_30m_observations, hours):
    """Gets the standard deviation of the list over the last number of hours"""
    number_observations = hours * 2  # TODO: assert that read interval is 30m
    trimmed_list = list_of_30m_observations[:number_observations]
    try:
        return numpy.std(trimmed_list)
    except TypeError as e:
        trimmed_list = [float(l) for l in trimmed_list]
        return numpy.std(trimmed_list)

@log
def col_names():
    """Returns a string containing the names of the columns of the output file"""
    return "duration," + \
           "temp_mean," + \
           "temp_stddev," + \
           "rel_humidity_mean," + \
           "rel_humidity_stddev," + \
           "rain_mean"

@log
def line_item(duration):
    """Gets the values to write to the file"""
    return "%s,%s,%s,%s,%s,%s" % (
        duration,
        get_rolling_average(temp_observations, duration),
        get_std_dev(temp_observations, duration),
        get_rolling_average(humidity_observations, duration),
        get_std_dev(humidity_observations, duration),
        get_rolling_average(rain_observations, duration)
    )

durations = (72, 48, 24, 12, 6)

# r = requests.get(r'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94294.json')
logger.debug("url  = %s" % args.gauge_url)
r = requests.get(parse_url(args.gauge_url))
data_list= r.json()['observations']['data']

assert len(data_list)>=max(durations)*2, "Analysis is asking for a number of data points (%s) that is longer than the available data (%s)" % (
        max(durations)*2,
        len(data_list)
    )


if args.verbose:
    print("")
    print("gauge_url = %s" % "TODO")
    gauge_name = data_list[0]['name']
    print("gauge_name = %s" % gauge_name)
    # most recent temperature observation
    print("Temperature = %s at %s" % (data_list[0]['air_temp'], data_list[0]['local_date_time']))
    print("")

temp_observations = [observation['air_temp'] for observation in data_list]
humidity_observations = [observation['rel_hum'] for observation in data_list]
rain_observations = [observation['rain_trace'] for observation in data_list]

if args.output:
    # print("writing to %s" % args.output)
    with open(args.output, 'w') as file:
        file.write(col_names() + "\n")
        for duration in durations:
            file.write(line_item(duration) + "\n")
else:
    print(col_names())
    for duration in durations:
        print(line_item(duration))


# for column in data_list[0]:
#     print(column)


