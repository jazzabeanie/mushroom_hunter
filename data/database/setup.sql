---------------------------------------------------------------------------
--
-- setup.sql
--    Performs setup for the mhunter.py app
--
---------------------------------------------------------------------------

-----------------------------
-- Creating a table
--	Creates a table with all the attributes which will be needed to store data.
-----------------------------

-- -- Originally I was going to only save a selection of columns, and give them meaningful names:
--   local_time date,
--   utc_time date,
--   feels_like real,
--   cloud varchar(32),
--   cloud_base_m int,
--   cloud_oktas int,
--   cloud_type varchar(32),
--   cloud_type_id int,
--   delta_t real, -- https://en.wikipedia.org/wiki/Wet-bulb_temperature#Wet-bulb_depression
--   wet_bulb_temp real, -- calculated from delta_t
--   gust_kmh int,
--   gust_kt int,
--   temp real,
--   dew_point real,
--   pressure real,
--   pressure_msl real,
--   rain_since_9 real,
--   humidity int,

CREATE TABLE Townsville (
  sort_order int,
  wmo int,
  name varchar(128),
  history_product varchar(16),
  local_date_time varchar(16),
  local_date_time_full varchar(16),
  aifstime_utc varchar(16),
  lat real,
  lon real,
  apparent_t real,
  cloud varchar(32),
  cloud_base_m int,
  cloud_oktas int,
  cloud_type varchar(32),
  cloud_type_id int,
  delta_t real,
  gust_kmh int,
  gust_kt int,
  air_temp real,
  dewpt real,
  press real,
  press_msl real,
  press_qnh real,
  press_tend varchar(4),
  rain_trace real,
  rel_hum int,
  sea_state varchar(32),
  swell_dir_worded varchar(32),
  swell_height varchar(32),
  swell_period varchar(32),
  vis_km int,
  weather varchar(64),
  wind_dir varchar(4),
  wind_spd_kmh int,
  wind_spd_kt int
);