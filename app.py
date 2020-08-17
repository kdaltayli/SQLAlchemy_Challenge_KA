
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,inspect
import numpy as np
import datetime as dt
import pandas as pd

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify

engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")
Base= automap_base()

Base.prepare(engine, reflect=True)

Station= Base.classes.station
Measurement= Base.classes.measurement

# Create an app
app= Flask(__name__)


@app.route("/")
def welcome():
    return (
        f" Welcome to my Home...!<br/>"
        f"Available Routes:<br/> "
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    # Return the JSON representation of your dictionary.

    results= session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    dates_and_pre_sco = []
    for date,prcp in results:
        result_dict = {}
        result_dict["date"] = date
        result_dict["prcp"] = prcp

        dates_and_pre_sco.append(result_dict)

    return jsonify(dates_and_pre_sco)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    session=Session(engine)
    result_st=session.query(Station.name, Station.station).all()

    session.close()

  # Convert list of tuples into normal list
    all_stat = list(np.ravel(result_st))

    return jsonify(all_stat)
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
#   Query the dates and temperature observations of the most active station for the last year of data.
    active_station= session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    result=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==active_station[0][0]).all()
#   Return a JSON list of temperature observations (TOBS) for the previous year.
    all_data= list(np.ravel(result))

    return jsonify(all_data)

@app.route("/api/v1.0/<start>")
def climate_start(start):
    session=Session(engine)
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    result= session.query(Measurement.date, func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs),2)).filter(Measurement.station >= start_dt).all()
    session.close()

    
    
    result_list= []

    for date, min,max,avg in result:
        result_dic={}
        result_dic['Start Date']=start_dt
        result_dic['TMIN']=min
        result_dic['TMAX']=max
        result_dic['TAVG']=avg

        result_list.append(result_dic)

        return jsonify(result_list)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session=Session(engine)
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    # for a given start or start-end range.
 
   
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    result= session.query(Measurement.date, func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs),2)).\
        filter(Measurement.date>=start_dt).filter(Measurement.date<=end_dt).all()
    session.close()

    json_list=[]

    for date,min,max,avg,date in result:
        json_dict={}
        json_dict['Start Date']=start_dt
        json_dict['End Date']=end_dt
        json_dict['TMIN']=min
        json_dict['TMAX']=max
        json_dict['TAVG']=avg
        json_list.append(json_dict)

    return jsonify(json_list)




# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)