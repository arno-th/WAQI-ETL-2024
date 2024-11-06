import logging
from typing import TYPE_CHECKING

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

logger = logging.getLogger("airflow.task")

@task()
def get_available_stations_() -> list[dict]:
    import json

    if TYPE_CHECKING:
        from requests import Response

    from airflow.models import Variable
    from airflow.providers.http.hooks.http import HttpHook

    # Set up hook
    waqi_api_token = Variable.get("waqi_api_token")
    httphook = HttpHook(
        method="GET",
        http_conn_id="waqi_api",
    )

    # Send request to API
    lat_long_bounds = "-10.6,113.2,-43.6,153.6" # Bounds for Australia
    logger.info(f"Geo-coordinates (lat1, long1, lat2, long2): {lat_long_bounds}")
    response: Response = httphook.run(
        endpoint=f"/map/bounds?latlng={lat_long_bounds}&token={waqi_api_token}",
    )

    # Process response
    logger.debug(f"Response status: {response.status_code}")
    if not response.ok:
        response.raise_for_status()
    data = json.loads(response.text)

    # Process response data
    stations = data["data"]
    logger.info(f"Stations: {stations}")
    stations_filtered = [
        {"name":station["station"]["name"],
         "id":station["uid"]}
        for station in stations
    ]
    logger.info(f"Found {len(stations_filtered)} stations in Australia")
    return stations_filtered

@task()
def get_station_data(stations: list[dict]) -> list[dict]:
    import json

    if TYPE_CHECKING:
        from requests import Response

    from airflow.models import Variable
    from airflow.providers.http.hooks.http import HttpHook

    # Set up hook
    waqi_api_token = Variable.get("waqi_api_token")
    httphook = HttpHook(
        method="GET",
        http_conn_id="waqi_api",
    )

    # Retrieve raw data from API and store raw data
    stations_data = []
    logger.info(f"Retrieving data for {len(stations)} stations")
    for station in stations:
        logger.info(f'::group::Retrieving data for {station["name"]}')
        endpoint = f'/feed/@{station["id"]}/?token={waqi_api_token}'
        logger.info(f"Endpoint: {endpoint}")

        # Send request to API
        response: Response = httphook.run(endpoint=endpoint)
        logger.debug(f"Response status: {response.status_code}")
        if not response.ok:
            response.raise_for_status()
        data = json.loads(response.text)
        logger.info(f"Response data: {data}")

        # Check response status
        if "data" not in data or "status" not in data:
            logger.error(f"No status or data in response. Response: {data}")
            logger.info("::endgroup::")
            continue
        if data["status"] != "ok":
            logger.error(f"Could not find station. Reason: {data['data']}")
            logger.info("::endgroup::")
            continue

        # Store station data
        station_data = data["data"]
        logger.info(f"Station: {station_data}")
        stations_data.append(station_data)
        logger.info("::endgroup::")

    logger.info(f"Retrieved data for {len(stations_data)} of {len(stations)} stations")
    return stations_data

@task()
def process_air_quality_data(stations_data: list[dict]) -> list[dict]:
    refined_data = []
    num_stations = len(stations_data)
    logger.info(f"Processing data for {num_stations} stations")
    for idx, station_data in enumerate(stations_data):
        logger.info(f"::group::Processing station {idx+1}/{num_stations}")

        # Get the timestamp of when the data was collected in iso format
        time_data: dict = station_data.get("time")
        date_iso_str = time_data.get("iso") if time_data else None

        # Refine the data to only the datapoints we want
        refined_data.append({
            "station_id": station_data.get("idx"),
            "station_name": station_data["city"].get("name"),
            "dominant_pollutant": station_data.get("dominentpol"),
            "aqi": station_data.get("aqi"),
            "data_timestamp": date_iso_str,
        })
        logger.info(f"Refined station data: {refined_data[-1]}")
        logger.info("::endgroup::")
    return refined_data

@task()
def load_dwh(transformed_data: list[dict]) -> None:
    from src.clickhouse import get_clickhouse_con
    con = get_clickhouse_con()

    aqi_table = "air_quality"
    aq_table = con.table(aqi_table)
    logger.info(aq_table.execute())

    logger.info(f"Inserting into '{aqi_table}': {transformed_data}")
    con.insert(aqi_table, transformed_data)
    logger.info(aq_table.execute())

# Define the Airflow DAG
default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
}


@dag(
    dag_id="waqi_air_quality_etl",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
)
def etl_dag() -> None:
    station_names = get_available_stations()
    stations_data_raw = get_station_data(station_names)
    stations_data_transformed = process_air_quality_data(stations_data_raw)

    station_names >> stations_data_raw >> stations_data_transformed >> load_dwh(stations_data_transformed) # noqa: E501


etl_dag()
