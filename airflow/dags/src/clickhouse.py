import ibis
import ibis.backends
import ibis.backends.clickhouse

from airflow.models import Variable


def get_clickhouse_con() -> ibis.backends.clickhouse.Backend:
    clickhouse_host = Variable.get("clickhouse_host")
    clickhouse_port = Variable.get("clickhouse_port")
    clickhouse_user = Variable.get("clickhouse_user")
    clickhouse_pwd = Variable.get("clickhouse_pword")
    con = ibis.clickhouse.connect(
        host=clickhouse_host,
        port=clickhouse_port,
        user=clickhouse_user,
        password=clickhouse_pwd,
    )
    return con
