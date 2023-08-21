# Import the dependencies.
from flask import Flask, jsonify
#################################################
# Database Setup
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def home():
    return (
    f"Welcome to the Hawaii Weather API!<br/>"
    f"Available routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/start_date<br/>"
    f"/api/v1.0/start_date/end_date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
    
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
    
    query_results = session.query(Measurement.date, Measurement.prcp)\
                          .filter(Measurement.date >= one_year_ago_str)\
                          .order_by(Measurement.date).all()
    session.close()
    precipitation_data = {}
    for date, prcp in query_results:
        precipitation_data[date] = prcp
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    station_names = session.query(Station.station).all()
    session.close()
    station_list = [station[0] for station in station_names]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)
        
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station))\
                             .group_by(Measurement.station)\
                             .order_by(func.count(Measurement.station).desc())\
                             .first()[0]
    
    query_results = session.query(Measurement.date, Measurement.tobs)\
                          .filter(Measurement.station == active_stations)\
                          .filter(Measurement.date >= one_year_ago_str)\
                          .all()
    
    session.close()

    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in query_results]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start(start):

    start_date = datetime.strptime(start, '%Y-%m-%d')
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start_date)\
                      .all()
    
    temperature_stats = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    session.close()

    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_range(start, end):
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start_date)\
                      .filter(Measurement.date <= end_date)\
                      .all()
    
    temperature_stats = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    session.close()

    return jsonify(temperature_stats)
 
    
if __name__ == "__main__":
    app.run(debug=True)
