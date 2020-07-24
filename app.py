import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime 

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawalii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def main():
    """Lists all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
         
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()



    precipitation= []
    for result in prcp_results:
        row = {"date":"prcp"}
        row["date"] = result[0]
        row["prcp"] = float(result[1])
        precipitation.append(row)
        return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():

   station_results = session.query(Station.station, Station.station_name).group_by(Station.station).all()
   station_list = list(np.ravel(station_results))
   return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    
    tobs_results = session.query(Measurement.station, Measurement.tobs).filter(Measurement.date.between('2016-08-01', '2017-08-01')).all()

    tobs_list=[]
    for tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["station"] = tobs[0]
        tobs_dict["tobs"] = float(tobs[1])
       
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/calc_temps/<start>")

def calc_temps(start='start_date'):
    start_date = datetime.strptime('2016-08-01', '%Y-%m-%d').date()
    start_results = session.query(func.max(Measurement.tobs), \
                            func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date) 
    
    start_tobs = []
    for tobs in start_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])
        
        start_tobs.append(tobs_dict)

    return jsonify(start_tobs)

@app.route("/api/v1.0/calc_temps/<start>/<end>")

def calc_temps_2(start='start_date', end='end_date'):      
    start_date = datetime.strptime('2016-08-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2017-08-01', '%Y-%m-%d').date()

    start_end_results=session.query(func.max(Measurement.tobs).label("max_tobs"), \
                      func.min(Measurement.tobs).label("min_tobs"),\
                      func.avg(Measurement.tobs).label("avg_tobs")).\
                      filter(Measurement.date.between(start_date , end_date))   

    start_end_tobs = []
    for tobs in start_end_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        start_end_tobs.append(tobs_dict)
    
    return jsonify(start_end_tobs)

if __name__ == '__main__':
    app.run(debug=True)

