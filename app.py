# Import dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

### 
# SQLAlchemy
###

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
stations = Base.classes.station

###
# Flask (not just for drinking)
###

app = Flask(__name__)

# Routes

# Home
@app.route('/')
def home():
    return (
        f'Welcome to the bestest Climate App<br/>'
        f'Available routes are:<br/>'
        f"Precipitation: <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"List of Stations: <a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"Temperature data for past year: <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"Temperature data select date (yyyy-mm-dd): <a href='/api/v1.0/2016-08-23'>/api/v1.0/yyyy-mm-dd</a><br/>"
        f"Temperature data between select dates (yyyy-mm-dd): <a href='/api/v1.0/2016-08-23/2017-08-23'>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</a><br/>"
        f"Available dates: 2010-01-01 - 2017-08-23"
    )

# Precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Vroom vroom
    session = Session(engine)

    # Query
    precip_q = session.query(measurement.date, measurement.prcp).order_by(measurement.date.desc()).all()

    session.close()

    # Makin it do
    Precipitation = []
    for date, prcp in precip_q:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = prcp
        Precipitation.append(precip_dict)
    return jsonify(Precipitation)

# Wyld Stallyns Bongosero (Station)
@app.route('/api/v1.0/stations')
def station():
     # Vroom vroom
    session = Session(engine)

    # Query
    station_q = session.query(stations.name).all()

    session.close()

    # Makin it do
    Station = []
    for station in station_q:
        Station.append(station[0])
    return jsonify(Station)
   
# TOBS
@app.route('/api/v1.0/tobs')
def tobs():
     # Vroom vroom
    session = Session(engine)

    # Estab dates
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent[0], '%Y-%m-%d')
    one_year = dt.date(recent_date.year-1, recent_date.month, recent_date.day)


    # Query
    tobs_q = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()

    session.close()

    # Makin it do
    tobs_l = list(tobs_q)

    return jsonify(tobs_l)

# Start Date
@app.route('/api/v1.0/<start>')
def sdate(start):
    # Vroom vroom
    session = Session(engine)

    # Validation
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    earliest = session.query(measurement.date).order_by(measurement.date.asc()).first()
    sstart = dt.datetime.strptime(start, '%Y-%m-%d')
    rrecent = dt.datetime.strptime(recent[0], '%Y-%m-%d')
    eearliest = dt.datetime.strptime(earliest[0], '%Y-%m-%d')

    if ((sstart >= eearliest) and (sstart <= rrecent)):

        # Query
        low = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).all()
        high = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).all()
        avg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).all()

        session.close()

        # Makin it do
        response = [f'Lowest temp:{low}  Highest tem:{high}  Average temp:{avg}']
    
    else:
        response = [f'No data for that date, please select a date between {earliest[0]} and {recent[0]}']

    return jsonify(response)

# Start End
@app.route('/api/v1.0/<start>/<end>')
def end (start, end):
    # Vroom vroom
    session = Session(engine)

    # Validation
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    earliest = session.query(measurement.date).order_by(measurement.date.asc()).first()
    sstart = dt.datetime.strptime(start, '%Y-%m-%d')
    eend = dt.datetime.strptime(start, '%Y-%m-%d')
    rrecent = dt.datetime.strptime(recent[0], '%Y-%m-%d')
    eearliest = dt.datetime.strptime(earliest[0], '%Y-%m-%d')

    if ((sstart >= eearliest and eend <= rrecent) and (sstart <= eend)):

        # Query
        low = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        high = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
        avg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

        session.close()

        # Makin it do
        response = [f'Lowest temp:{low}  Highest tem:{high}  Average temp:{avg}']
    
    else:
        response = [f'No data for that date range, please select dates between {earliest[0]} and {recent[0]}']

    return jsonify(response)

if __name__ == "__main__":
  app.run(debug=True)  