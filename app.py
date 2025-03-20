# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt



last_year=dt.date(2017,8,23)-dt.timedelta(days=365)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def weather():
    return(
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    precipitation_dict={date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)
    

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    station_results=session.query(Station.name).all()
    session.close()
    stations_list=[station[0] for station in station_results]
    return jsonify(stations_list)

                     
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]  

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= last_year)\
        .order_by(Measurement.date).all()

    session.close()

    tobs_list = [{date: temp} for date, temp in results]
    
    return jsonify(tobs_list)  


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    session = Session(engine)

    
    sel = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ]

    
    if end:
        results = session.query(*sel)\
            .filter(Measurement.date >= start)\
            .filter(Measurement.date <= end)\
            .all()
    else:
        
        results = session.query(*sel)\
            .filter(Measurement.date >= start)\
            .all()

    session.close()

    
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temp_stats)

if __name__=="main":
    app.run(debug=True)

