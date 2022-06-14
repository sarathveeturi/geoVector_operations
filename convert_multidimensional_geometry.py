from datetime import datetime
import pandas as pd
import numpy as np
from matplotlib.pyplot import close
import psycopg2
from psycopg2 import sql, connect
import calendar
#time= datetime.now()

table_name="sample_postgis_output"
date = datetime.utcnow()
time = calendar.timegm(date.utctimetuple())

def convert(table_name, time):
    con = psycopg2.connect (host = "localhost",database="postgres",user = "postgres",password = "6949")
    cur = con.cursor()
    cur.execute("""ALTER TABLE {} ADD COLUMN t_wkb_geometry text;""".format(table_name))
    con.commit()



    con = psycopg2.connect (host = "localhost",database="postgres",user = "postgres",password = "6949")
    cur = con.cursor()
    #cur.execute("""UPDATE {} SET t_wkb_geometry= St_AsText(ST_Force4D(geom, 0, extract(epoch from (NOW()::time))));""".format(table_name))
    cur.execute("""UPDATE {} SET t_wkb_geometry= St_AsText(ST_Force4D(geom, 0, {}));""".format(table_name,time))
    con.commit()


convert(table_name, time)