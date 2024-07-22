"""Export data from query into DataFrame with local time as index.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

from datetime import datetime, timedelta

from influxdb_client.client.flux_table import TableList
import pandas as pd


class DataParser:
    def __init__(self, tables: TableList) -> None:
        self.tables = tables

    def _local_time(self, timestamps: set[datetime]):
        """Accounts for timezone offset, since InfluxDB stores data in UTC.

        Args:
            timestamps (list): A list of UTC timestamps.
        Returns:
            list: A list of timestamps in local time.
        """

        local_timestamps = []

        # current datetime along with timezone
        now = datetime.now().astimezone()

        # UTC offset in seconds
        offset = now.utcoffset()
        offset_seconds = offset.total_seconds() if offset is not None else 0
        local_offset = timedelta(seconds=offset_seconds)

        # add the offset to the timestamps
        for timestamp in timestamps:
            utc_time = pd.to_datetime(timestamp)
            local_time = utc_time + local_offset
            local_timestamps.append(local_time)

        return local_timestamps

    def into_dataframe(self) -> pd.DataFrame:
        """Parse the query into pd.DataFrame with time as index.

        Args:
            tables (list): The tables to turn into a DataFrame.
        Returns:
            pd.DataFrame: procured measurements as a DataFrame sorted by time.
        """
        read: dict[str, list[str | float]] = {}
        timestamps: set[datetime] = set()

        # unpacking the table
        for table in self.tables:
            for record in table.records:
                # get the measurements
                parameter = record.get_field()
                measurement = record.get_value()
                timestamps.add(record.get_time())

                # ensure every parameter is present in the dict
                if parameter not in read:
                    read[parameter] = []
                read[parameter].append(float(measurement))

        # convert timestamps to local time
        local_timestamps = self._local_time(timestamps)

        # if there is no time key, create one
        if 'time' not in read:
            read['time'] = []

        # add the timestamps to the data dict
        for timestamp in local_timestamps:
            read['time'].append(pd.to_datetime(timestamp))

        df = pd.DataFrame(read)
        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)

        return df
