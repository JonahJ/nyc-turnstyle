import numpy as np
import pandas as pd
from datetime import datetime
import os

SANITIZED_DIR = 'data_sanitized/'


class MTAReader:

    def __init__(self, file_name, data_str=None, output_dir=None, debug=False):
        self.file_name = file_name
        self.data_str = data_str
        self.debug = debug
        self.output_dir = output_dir
        if self.output_dir is None:
            self.output_dir = SANITIZED_DIR

        if self.debug is True:
            print('WARNING debug mode is true, not all data will be processed')

        self.max_n = 8  # Because guide says so and our analysis on one file confirmed

        self.raw_columns = []
        self.raw_data = pd.DataFrame([])
        self.merged_with_stations = pd.DataFrame([])
        self.df_pre_traffic = pd.DataFrame([])
        self.df = pd.DataFrame([])

        ''' better to pass in since using multiple times, but this thing is
        30 kb, so will ignore for now for modularity '''
        self.stations = pd.read_csv('data/stations_full.csv')

        self.read()

    def __del__(self):
        del self.df
        pass

    def getDF(self):
        ''' returns DF from reader '''
        return self.df

    def __generateColumns(self):
        ''' generates columns for raw read '''

        self.raw_columns = [
            "ControlArea",
            "RemoteUnit",
            "SCP"
        ]

        """ add in N extra fields, just as field description says """
        extra_cols = [
            "DATE",
            "TIME",
            "DESC",
            "ENTRIES",
            "EXITS",  # typo on their part, corrected `EXISTS` to `EXITS` for sanity
        ]

        for i_position_in_row in xrange(self.max_n):
            position_in_row = str(i_position_in_row)
            for extra_col in extra_cols:
                self.raw_columns.append(extra_col + "_" + position_in_row)

        print('Generated columns')

    def __readFile(self):
        ''' read in file data '''

        if self.data_str is not None:
            self.raw_data = pd.read_csv(self.data_str, names=self.raw_columns)
        else:
            self.raw_data = pd.read_csv(self.file_name, names=self.raw_columns)

        # print(self.raw_data.head())
        # print(self.raw_data.dtypes)
        print('Read in raw data')

    def __joinStations(self):
        ''' join in stations '''

        self.merged_with_stations = pd.merge(
            self.raw_data,
            self.stations,
            left_on=["ControlArea", "RemoteUnit"],
            right_on=["Booth", "Remote"],
            how="inner"
        )

        ''' confirm that we have no missing data '''
        # print("DF originally", len(self.raw_data))
        # print("DF With Stations", len(self.merged_with_stations))
        num_missing = len(self.raw_data) - len(self.merged_with_stations)

        if num_missing != 0:
            raise 'Error Merging %d missing' % (num_missing)
        ''' get rid of the stuff we no longer need '''
        del self.stations
        del self.raw_data

        print('Merged with stations')

    def __reduce(self):
        sanitized_rows = []

        for i_row, row in self.merged_with_stations.iterrows():

            if self.debug is True:
                if i_row > 5:
                    break

            for i_time_interval in xrange(self.max_n):
                time_interval = str(i_time_interval)

                """ only those which do not have NaN as this grouping """
                if pd.notnull(row['DATE_' + time_interval]) is False:
                    break

                ''' rename columns to be all same relative formatting. I like using dot operator better '''
                sanitized_row = {
                    "remote_unit": row["RemoteUnit"],
                    "scp": row["SCP"],
                    "control_area": row["ControlArea"],
                    "date": row['DATE_' + time_interval],
                    "odometer_entries": row["ENTRIES_" + time_interval],
                    "odometer_exits": row["EXITS_" + time_interval],
                    "description": row['DESC_' + time_interval],
                    "time": row['TIME_' + time_interval],

                    "division": row['Division'],
                    "line_name": row['Line Name'],
                    "station": row['Station'],
                    "created_by_human": row['created_by_human'],

                    "interval": i_time_interval,
                    "csv_row": i_row
                }

                sanitized_rows.append(sanitized_row)

        self.df_pre_traffic = pd.DataFrame(sanitized_rows)
        self.df_pre_traffic['file'] = self.file_name

        self.__correctTypes()

        print('Reduced')

    def __correctTypes(self):
        ''' correct df types '''

        try:
            """ datetimes """
            self.df_pre_traffic['datetime'] = pd.to_datetime(
                self.df_pre_traffic['date'] + self.df_pre_traffic['time'],
                format="%m-%d-%y%X"
            )
            self.df_pre_traffic['date'] = pd.to_datetime(
                self.df_pre_traffic['date'],
                format="%m-%d-%y"
            )

            del self.df_pre_traffic['time']

            """ numeric """
            self.df_pre_traffic['odometer_entries'] = self.df_pre_traffic['odometer_entries'].convert_objects(
                convert_numeric=True
            ).astype(int)
            self.df_pre_traffic['odometer_exits'] = self.df_pre_traffic['odometer_exits'].convert_objects(
                convert_numeric=True
            ).astype(int)

            print('Types corrected')
        except Exception as inst:
            print('Exception in correcting df types', inst)
            print('Writting df pre these changes to:', 'PRE_TYPES.csv')
            self.df_pre_traffic.to_csv('PRE_TYPES.csv', index=False)

    def __computeTraffic(self):
        ''' computes traffic and adds it to df '''

        time_series_analyzed_data = []
        df_by_grouping = self.df_pre_traffic.groupby(['station', 'remote_unit', 'scp'])
        for i, ((station, remote_unit, scp), data) in enumerate(df_by_grouping):
            # print(station, remote_unit, scp, len(data), data['datetime'].min(), data['datetime'].max())
            if self.debug is True:
                if i > 200:
                    break

            updated = data.copy(deep=True)  # pandas complains unless we deep copy it

            updated = updated.sort('datetime')
            updated['entries'] = updated.odometer_entries - updated.odometer_entries.shift(1)
            updated['exits'] = updated.odometer_exits - updated.odometer_exits.shift(1)
            updated['net_time'] = updated.datetime - updated.datetime.shift(1)
            updated['net_flow'] = updated.entries - updated.exits
            # updated['cummulative_flow'] = updated.entries + updated.exits

            time_series_analyzed_data.append(updated)
        del df_by_grouping
        self.df = pd.concat(time_series_analyzed_data)

        self.df['cummulative_flow'] = self.df.entries + self.df.exits

        print('Computted Traffic')

    def __dump(self):
        ''' write to file '''

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        output_date_format = '%Y-%m-%d'
        date_min = self.df.datetime.min()
        date_max = self.df.datetime.max()

        processed_file_name = '%s - %s' % (
            date_min.strftime(output_date_format),
            date_max.strftime(output_date_format)
        ) + '.csv'

        self.df.to_csv(self.output_dir + processed_file_name, index=False)

        print('Dumped to', processed_file_name)

    def __replaceBadOdometerChanges(self, keys):
        ''' put into a function, the work to go thru the df was being repeated so this should be MUCH quicker '''

        where = []
        for i_key, key in enumerate(keys):
            # if i_key > 1:
            #     break
            where.append(
                self.df[key] < 0
            )

        located = pd.concat(
            where,
            axis=1
        )

        located['replace'] = False
        for i_key, key in enumerate(keys):
            located['replace'] = located['replace'] | located[key]

        print('Fixing # rows:', len(located.loc[located['replace']]))

        for i_key, key in enumerate(keys):
            self.df.replace(
                self.df.loc[located['replace']][key].values,
                0,
                inplace=True
            )

        print('Replaced bad odemeter values')

    def __sanityCheck(self):
        ''' sanity check

        Trouble is we actually should have NaN values at this point, for the
        earliest datetimes, since nothing to subtract from
        '''

        ''' replace negative odometer readings '''
        self.__replaceBadOdometerChanges(['exits', 'entries', 'cummulative_flow'])

        pass

    def read(self):
        ''' reads in data, merges in stations, reforms into df '''

        print('Starting', self.file_name)

        ''' generate columns '''
        self.__generateColumns()

        ''' read in data '''
        self.__readFile()

        ''' join in stations '''
        self.__joinStations()

        ''' Reduce Dimensions '''
        self.__reduce()

        ''' compute traffic '''
        self.__computeTraffic()

        ''' error / sanity check '''
        self.__sanityCheck()

        ''' dump '''
        self.__dump()

        print('')


# if __name__ == "__main__":
#     # reader = MTAReader('data/turnstile_130803.txt')

#     # MTAReader('data/turnstile_130706.txt')

#     MTAReader('data/turnstile_130803.txt')
