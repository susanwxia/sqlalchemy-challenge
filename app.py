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
Base.prepare(engine, reflect=True)

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session:
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# Define a function that given the start and end date to calculate the min. temperature (`TMIN`), 
# avg. temperature (`TAVG`), and max. temperature (`TMAX`) for dates between the start and end date

def temp(start_d, end_d):

    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_d).filter(Measurement.date <= end_d).all()

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Surfs-up API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary"""

    print("Precipitation data for the recent year.")
    # The most recent data point in the database is 2017-08-23 according to the analysis
    # The date that one year from the most recent date:
    one_yr_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores for the recent year
    one_yr_prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_yr_ago).all()

    # Create dictionary:
    prcp_dict = {}
    for prcp_data in one_yr_prcp:
        prcp_dict[prcp_data[0]] = prcp_data[1]

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    stations = session.query(Station).all()

    stn_list = []
    for stn in stations:
        stn_dict = {}
        stn_dict["id"] = stn.id
        stn_dict["station"] = stn.station
        stn_dict["name"] = stn.name
        stn_dict["latitude"] = stn.latitude
        stn_dict["longitude"] = stn.longitude
        stn_dict["elevation"] = stn.elevation
        stn_list.append(stn_dict)

    return jsonify(stn_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""

    # The most recent data point in the database is 2017-08-23 according to the analysis
    # The date that one year from the most recent date:
    one_yr_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Most activate station in the previous analysis: USC00519281
    one_yr_tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= one_yr_ago).\
    filter(Measurement.station == 'USC00519281').all()

    print("temperature observations (TOBS) for the previous year for station: USC00519281")
    tobs_list = []
    for tobs_stn in one_yr_tobs:
        tobs_dict = {}
        tobs_dict["date"] = tobs_stn.date
        tobs_dict["tobs"] = tobs_stn.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):

    # The most recent data point in the database is 2017-08-23 according to the analysis
    max_date = dt.date(2017, 8, 23)

    temp_query = temp(start, max_date)

    temp_list = []
    temp_list.append({"TMIN": temp_query[0][0], "TAVG": temp_query[0][1], "TMAX": temp_query[0][2]})

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    temp_query = temp(start, end)

    temp_list = []
    temp_list.append({"TMIN": temp_query[0][0], "TAVG": temp_query[0][1], "TMAX": temp_query[0][2]})

    return jsonify(temp_list)


if __name__ == "__main__":
    app.run(debug=True)
