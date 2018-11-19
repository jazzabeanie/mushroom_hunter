import requests
import argparse
import numpy

parser = argparse.ArgumentParser(description="Analyses recent BOM data to determine whether it's a good time to forrage for mushrooms.")
# mandatory arguments:
parser.add_argument("gauge_id", help="The itentifier for the BOM observation gauge you want to querry. The tool will put it into this urL: http://www.bom.gov.au/products/IDQ60801/IDQ60801.GAUGE.shtml ")
# optional arguments:
parser.add_argument("-o",
                    "--output",
                    action="store",
                    help="specifies output to write the results to. If not provided, results will be written to std out")
args = parser.parse_args()

# TODO: think about security if I expose this publically. -- Bobby Tables

def get_rolling_average(list_of_30m_observations, hours):
    """Gets the average value in the list over the last number of hours"""
    number_observations = hours * 2  # TODO: assert that read interval is 30m
    trimmed_list = list_of_30m_observations[:number_observations]
    try:
        return sum(trimmed_list)/len(trimmed_list)
    except TypeError as e:
        trimmed_list = [float(l) for l in trimmed_list]
        return sum(trimmed_list)/len(trimmed_list)

def get_std_dev(list_of_30m_observations, hours):
    """Gets the standard deviation of the list over the last number of hours"""
    number_observations = hours * 2  # TODO: assert that read interval is 30m
    trimmed_list = list_of_30m_observations[:number_observations]
    try:
        return sum(trimmed_list)/len(trimmed_list)
    except TypeError as e:
        trimmed_list = [float(l) for l in trimmed_list]
        return sum(trimmed_list)/len(trimmed_list)


# print("gauge_id = %s" % args.gauge_id)
#
# requests help: http://docs.python-requests.org/en/master/
r = requests.get(r'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94294.json')
data_list= r.json()['observations']['data']

gauge_name = data_list[0]['name']
# print("gauge_name = %s" % gauge_name)
#
# print("Temperature = %s at %s" % (data_list[0]['air_temp'], data_list[0]['local_date_time']))

temp_observations = [observation['air_temp'] for observation in data_list]
humidity_observations = [observation['rel_hum'] for observation in data_list]
rain_observations = [observation['rain_trace'] for observation in data_list]
# temps_24h = [observation['air_temp'] for observation in data_list][:48] # should assert that read interval is 30 minutes
# print("24h average temperature = %s" % (sum(temps_24h)/len(temps_24h)))

# print("48h average temperature = %s" % get_rolling_average(temp_observations, 48))
# print("24h average temperature = %s" % get_rolling_average(temp_observations, 24))
# print("12h average temperature = %s" % get_rolling_average(temp_observations, 12))
# print("6h average temperature = %s" % get_rolling_average(temp_observations, 6))
#
# print("")

if args.output:
    # print("writing to %s" % args.output)
    with open(args.output, 'w') as file:
        file.write("duration,mean_temp,rel_humidity,rain\n")
        for duration in (48, 24, 12, 6):
            file.write("%s,%s,%s,%s\n" % (duration, get_rolling_average(temp_observations, duration), get_rolling_average(humidity_observations, duration), get_rolling_average(rain_observations, duration)))
else:
    print("duration,mean_temp,rel_humidity,rain")
    for duration in (48, 24, 12, 6):
        print("%s,%s,%s,%s" % (duration, get_rolling_average(temp_observations, duration), get_rolling_average(humidity_observations, duration), get_rolling_average(rain_observations, duration)))


# for column in data_list[0]:
#     print(column)


