# Introduction
This project is a sample ETL and database.
We use load data colelcted by stations from the World's Air Pollution API, and load relevant data points into a local database.

# Platform
The ETL platform is built using docker, we create 2 containers; one for orchestration and one for the database.
The containers were separated as each performs a separate function and so should be easily replaced by a different service shouuld the need arise.

## Orchestration
Apache Airflow was chosen as the orchestration tool of choice. The initial docker compose file was taken from an example from the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html). 
Some modifications were made to the initial file:

- Changed celery broker from Redis backend to RabbitMQ backend (due to less restrictive licensing)
- Moved the Airflow volumes into defined Docker volumes (previously filesystem volumes)
- Created .env file to contain sensitive information (see `./airflow/.env-sample` for an example of the required setup)

The advantage of using the example docker file over creating a single simple docker container for Airflow is the scalability the Celery broker and workers offer.

## API
The api is the [World's Air Pollution API](https://waqi.info/), which is a free to use API.
The docs for the API can be found [here](https://aqicn.org/json-api/doc/)

## Database
The database container runs a single clickhouse instance (this could be augmented to use a more scalable container with a scheduler and workers similar to the Airflow container - however that is beyond the current scope of this project)
See the following [Github repo](https://github.com/ClickHouse/examples/blob/main/docker-compose-recipes/README.md) for further examples of how to set up various Clickhouse configurations.