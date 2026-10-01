import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.app.config import settings

logger = logging.getLogger("influx_db")

class InfluxDBManager:
    def __init__(self):
        self.client = None
        self.write_api = None
        self.query_api = None
        self._init_client()

    def _init_client(self):
        try:
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.write_api import SYNCHRONOUS
            self.client = InfluxDBClient(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            logger.info("Connected to InfluxDB v2 successfully.")
        except Exception as e:
            logger.warning(f"InfluxDB connection unavailable ({e}). Operating in memory metric mode.")

    def write_point(self, measurement: str, tags: Dict[str, str], fields: Dict[str, Any], timestamp=None):
        if self.write_api:
            try:
                from influxdb_client import Point
                point = Point(measurement)
                for k, v in tags.items():
                    point.tag(k, v)
                for k, v in fields.items():
                    if isinstance(v, (int, float, bool, str)):
                        point.field(k, v)
                self.write_api.write(bucket=settings.INFLUXDB_BUCKET, record=point)
            except Exception as e:
                logger.error(f"Failed to write to InfluxDB: {e}")
        else:
            logger.debug(f"[INFLUX MOCK WRITE] {measurement} tags={tags} fields={fields}")

influx_db = InfluxDBManager()
