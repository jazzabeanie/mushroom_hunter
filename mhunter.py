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
        logger.debug(f"""calling {func.__name__}(args={args}, kwargs={kwargs})""")
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


@log
def col_names():
    """Returns a string containing the names of the columns of the output file"""
    return "duration," + \
           "temp_mean," + \
           "temp_stddev," + \
           "rel_humidity_mean," + \
           "rel_humidity_stddev," + \
           "rain_total"



class Station:
    def __init__(self, url):
        self._url = url
        self._request = requests.get(parse_url(url))
        self._data_list= self._request.json()['observations']['data']
        self._durations = (72, 48, 24, 12, 6)
        assert len(self._data_list)>=max(self._durations)*2, "Analysis is asking for a number of data points (%s) that is longer than the available data (%s)" % (
                max(self._durations)*2,
                len(self._data_list)
            )
        self._humidity_observations = [observation['rel_hum'] for observation in self._data_list]
        self._rain_observations = [observation['rain_trace'] for observation in self._data_list]

    def _get_rolling_average(self, list_of_30m_observations, hours):
        """Gets the average value in the list over the last number of hours"""
        number_observations = hours * 2  # TODO: assert that read interval is 30m
        trimmed_list = list_of_30m_observations[:number_observations]
        try:
            return numpy.mean(trimmed_list)
        except TypeError as e:
            trimmed_list = [float(l) for l in trimmed_list]
            return numpy.mean(trimmed_list)

    def _get_std_dev(self, list_of_30m_observations, hours):
        """Gets the standard deviation of the list over the last number of hours"""
        number_observations = hours * 2  # TODO: assert that read interval is 30m
        trimmed_list = list_of_30m_observations[:number_observations]
        try:
            return numpy.std(trimmed_list)
        except TypeError as e:
            trimmed_list = [float(l) for l in trimmed_list]
            return numpy.std(trimmed_list)

    def _get_total_rain(self, hours):
        """Gets the total rainfall over the duration passed in as an argument"""
        number_observations = hours * 2
        values_only = list(filter(lambda x: x != '-', self._rain_observations))
        rain_since_last_reading = self._cumulative_to_distinct(values_only)
        value_over_duration = sum(rain_since_last_reading[0:number_observations])
        return value_over_duration

    def _cumulative_to_distinct(self, cumulative_list):
        """changes the rain readings to be the amount of rain since the last reading instead of since 9am"""
        distinct_list = []
        for i in range(len(cumulative_list)):
            if i==len(cumulative_list)-1:
                break
            new = float(cumulative_list[i])
            old = float(cumulative_list[i+1])
            if old>new:
                # TODO: assert time is 9:30am if readings are in 30 minute
                # intervals
                distinct_list.append(new)
            else:
                distinct_list.append(new-old)
        return distinct_list

    def graph(self, observations, interval):
        import plotly.offline as py
        import plotly.graph_objs as go
        trace = go.Scatter(
            x = list(range(0, len(observations)*interval, interval)),
            y = observations
        )
        data = [trace]
        py.plot(data, filename='temperature_graph')

    @property
    def url(self):
        return self._url

    @property
    def durations(self):
        return self._durations

    @property
    def recent_humidity(self):
        return self._data_list[0]['rel_hum']

    @property
    def recent_temp(self):
        return self._data_list[0]['air_temp']

    @property
    def recent_time(self):
        return self._data_list[0]['local_date_time']

    @property
    def gauge_name(self):
        return self._data_list[0]['name']

    @property
    def temp_observations(self):
        return [observation['air_temp'] for observation in self._data_list]

    @log
    def line_item(self, duration):
        """Gets the values to write to the file"""
        return "%s,%s,%s,%s,%s,%s" % (
            duration,
            self._get_rolling_average(self.temp_observations, duration),
            self._get_std_dev(self.temp_observations, duration),
            self._get_rolling_average(self._humidity_observations, duration),
            self._get_std_dev(self._humidity_observations, duration),
            self._get_total_rain(duration)
        )


if __name__ == "__main__":
    reading = Station(args.gauge_url)


    if args.verbose:
        print("")
        print(f"gauge_url = {reading.url}")
        print(f"gauge_name = {reading.gauge_name}")
        print(f"As of {reading.recent_time}:")
        print(f"  temp: {reading.recent_temp}")
        print(f"  humidity: {reading.recent_humidity}")
        print("")

    if args.output:
        logger.debug("writing table to %s" % args.output)
        with open(args.output, 'w') as file:
            file.write(col_names() + "\n")
            for duration in reading.durations:
                file.write(reading.line_item(duration) + "\n")
    else:
        print(col_names())
        for duration in reading.durations:
            print(reading.line_item(duration))


