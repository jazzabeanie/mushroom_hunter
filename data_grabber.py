import mhunter
import psycopg2
import logging

logger = logging.getLogger('data_grabber')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('data_grabber.log')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

conn = psycopg2.connect("dbname=bom user=jaredjohnston")

cur = conn.cursor()

observation_stations = {
    'townsville': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94294.json',
    'alva_beach': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.95296.json',
    'ayr': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.95295.json',
    'bowen_airport_aws': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94383.json',
    'cape_ferguson': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94297.json',
    'ingham': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.95291.json',
    'mout_stuart': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94272.json',
    'townsville_fanning_river': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94273.json',
    'woolshed': 'http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.95293.json'}

for gauge_name, url in observation_stations.items():
    logger.debug(f"getting data for {gauge_name} at {url}")

    gauge = mhunter.Station(url)

    cur.execute("SELECT max(local_date_time_full) FROM {}".format(gauge_name))
    latest_reading = cur.fetchone()[0]
    logger.debug(f"last saved reading: {latest_reading}")

    try:
        existing_position = gauge.dates.index(latest_reading)
        logger.debug(f"  All available observations are new")
    except ValueError as e:
        # This means there is no overlapping data
        existing_position = None

    new_data = gauge.data_list[:existing_position]

    logger.debug(f"number of new observations since last reading({latest_reading}): {len(new_data)}")

    logger.debug(f"new observations at: {[e['local_date_time'] for e in new_data]}")

    for entry in new_data:
        def parse(v):
            if v == "-":
                return None
            else:
                return v

        # entry_parsed = dict([(k, parse(v)) for k, v in ])
        entry_parsed = {k: parse(v) for k, v in entry.items()}
        cur.execute("""
                    INSERT INTO {} (sort_order, wmo, name, history_product, local_date_time, local_date_time_full, aifstime_utc, lat, lon, apparent_t, cloud, cloud_base_m, cloud_oktas, cloud_type, cloud_type_id, delta_t, gust_kmh, gust_kt, air_temp, dewpt, press, press_msl, press_qnh, press_tend, rain_trace, rel_hum, sea_state, swell_dir_worded, swell_height, swell_period, vis_km, weather, wind_dir, wind_spd_kmh, wind_spd_kt)
                    VALUES (%(sort_order)s, %(wmo)s, %(name)s, %(history_product)s, %(local_date_time)s, %(local_date_time_full)s, %(aifstime_utc)s, %(lat)s, %(lon)s, %(apparent_t)s, %(cloud)s, %(cloud_base_m)s, %(cloud_oktas)s, %(cloud_type)s, %(cloud_type_id)s, %(delta_t)s, %(gust_kmh)s, %(gust_kt)s, %(air_temp)s, %(dewpt)s, %(press)s, %(press_msl)s, %(press_qnh)s, %(press_tend)s, %(rain_trace)s, %(rel_hum)s, %(sea_state)s, %(swell_dir_worded)s, %(swell_height)s, %(swell_period)s, %(vis_km)s, %(weather)s, %(wind_dir)s, %(wind_spd_kmh)s, %(wind_spd_kt)s)
                    """.format(gauge_name),
                    entry_parsed) # more info: http://initd.org/psycopg/docs/usage.html

    logger.info(f"inserted {len(new_data)} new items into {gauge_name}")

conn.commit()

cur.close()
conn.close()
