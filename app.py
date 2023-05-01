# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes!:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations,<br/>"
        f"/api/v1.0/tobs,<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation of each date over the previous year"""
    # Query all precipitations and dates
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    preYear = dt.datetime.strptime(lastDate,'%Y-%m-%d').date() - dt.timedelta(365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= preYear).all()
                    
    # Create a dictionary from the row data and append to a list of precipitations
    precipitations = {date: prcp for date, prcp in precipitation}
    session.close() 

    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def names():
    """Return a list of all stations"""
    # Query all stations
    mas = session.query(Measurement.station).\
        group_by(Measurement.station).all()
    stations = list(np.ravel(mas))

    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperature():
    """Return a list of temperatures and dates of previous year of most active station"""
    # Query most active station temperature and dates of previous year
    mas = session.query(Measurement.station,func.count()).\
    group_by(Measurement.station).\
    order_by(func.count().desc()).all()
    lastDate_station = session.query(Measurement.date).order_by(Measurement.date.desc()).\
        filter(Measurement.station == mas[0][0]).first()[0]
    preYear_station = dt.datetime.strptime(lastDate_station,'%Y-%m-%d').date() - dt.timedelta(365)
    active = session.query(Measurement.date,Measurement.tobs).\
         filter(Measurement.date > preYear_station, Measurement.station==mas[0][0]).all()
    temp_active = list(np.ravel(active))
    temp_active

    session.close()

    return jsonify(temp_active)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_limits(start=None, end=None):
    """Find the Max, Min, and Average temperatures for all dates greater than or equal to the start date, or a 404 if not."""
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start, '%Y-%m-%d').date()
        results = session.query(*selection).\
                filter(Measurement.date>= start).all()
        session.close()
        temp_active = list(np.ravel(results))
        return jsonify(temp_active)
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end = dt.datetime.strptime(end, '%Y-%m-%d').date()
    results = session.query(*selection).\
                filter(Measurement.date>= start).\
                filter(Measurement.date <= end).all()
    session.close()
    temp_active = list(np.ravel(results))
    return jsonify(temp_active=temp_active)


if __name__ == "__main__":
    app.run(debug=True)