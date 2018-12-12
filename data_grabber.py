import mhunter
import psycopg2

conn = psycopg2.connect("dbname=bom user=jaredjohnston")

cur = conn.cursor()

townsville = mhunter.Station("http://www.bom.gov.au/fwo/IDQ60801/IDQ60801.94294.json")

for entry in townsville.data_list:
    print(entry)
    # TODO: INSERT into the database
    # See an example working with dictionaries here: http://initd.org/psycopg/docs/usage.html
