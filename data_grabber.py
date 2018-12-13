import mhunter
import psycopg2

conn = psycopg2.connect("dbname=bom user=jaredjohnston")

cur = conn.cursor()

townsville = mhunter.Station("http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94294.json")

for entry in townsville.data_list:
    # print(entry)

    cur.execute("""
                INSERT INTO townsville (sort_order, wmo, name, history_product, local_date_time, local_date_time_full, aifstime_utc, lat, lon, apparent_t, cloud, cloud_base_m, cloud_oktas, cloud_type, cloud_type_id, delta_t, gust_kmh, gust_kt, air_temp, dewpt, press, press_msl, press_qnh, press_tend, rain_trace, rel_hum, sea_state, swell_dir_worded, swell_height, swell_period, vis_km, weather, wind_dir, wind_spd_kmh, wind_spd_kt)
                VALUES (%(sort_order)s, %(wmo)s, %(name)s, %(history_product)s, %(local_date_time)s, %(local_date_time_full)s, %(aifstime_utc)s, %(lat)s, %(lon)s, %(apparent_t)s, %(cloud)s, %(cloud_base_m)s, %(cloud_oktas)s, %(cloud_type)s, %(cloud_type_id)s, %(delta_t)s, %(gust_kmh)s, %(gust_kt)s, %(air_temp)s, %(dewpt)s, %(press)s, %(press_msl)s, %(press_qnh)s, %(press_tend)s, %(rain_trace)s, %(rel_hum)s, %(sea_state)s, %(swell_dir_worded)s, %(swell_height)s, %(swell_period)s, %(vis_km)s, %(weather)s, %(wind_dir)s, %(wind_spd_kmh)s, %(wind_spd_kt)s)
                """,
                entry)

    # TODO: INSERT into the database
    # See an example working with dictionaries here: http://initd.org/psycopg/docs/usage.html

conn.commit()

cur.close()
conn.close()
