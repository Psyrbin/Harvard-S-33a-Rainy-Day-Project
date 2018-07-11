import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f = open("zips.csv")
reader = csv.reader(f)

first = True
for row in reader:
    #skip names of the columns
    if first:
        first = False
    else:
        #in case starting zeros are lost
        while len(row[0]) < 5:
            row[0] = '0' + row[0]

        db.execute("INSERT INTO zips (zip, city, state, latitude, longitude, population) VALUES (:x1, :x2, :x3, :x4, :x5, :x6)",
                    {"x1": row[0], "x2": row[1], "x3": row[2], "x4": row[3], "x5": row[4], "x6": row[5]})
db.commit()