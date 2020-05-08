import csv
import sys
import json

from base.exceptions import Error
from config.configfileparser import ConfigFileParser

class CSVToConfigFile:

    def __init__(self):
        pass

    def __call__(self,
                 config_file_path: str,
                 csv_file_path: str,
                 output_file_path: str):
        self.csv_file_path = csv_file_path
        self.config_file_path = config_file_path
        self.output_file_path = output_file_path
        self.parsed_items = {
            "INS": [],
            "INF": [],
            "FIX": [],
            "POI": [],
            "LIN": [],
            "PLA": []
        }
        with ConfigFileParser() as cfp:
            self.config = cfp(config_file_path)
        self.new = self.config.__source__
        self.parse_csv()
        self.write_new_config_file()

    def parse_csv(self):
        try:
            with open(self.csv_file_path, 'r') as f:
                c = csv.reader(f, delimiter=",")
                for row in c:
                    if row[0] in self.parsed_items:
                        self.parsed_items[row[0]].append(
                            [item for item in row[1:] if item != ""])
                    else:
                        print(f"Invalid spec: {row[0]}")
        except OSError as e:
            raise CSVToConfigFileOSError(self.csv_file_path, e)
        try:
            self.add_INS()
            self.add_INF()
            self.add_FIX()
            self.add_POI()
            self.add_LIN()
            self.add_PLA()
        except CSVToConfigFileValueError as e:
            sys.exit(e)
        except CSVToConfigFileIndexError as e:
            sys.exit(e)

    def add_INS(self):
        for idx, item in enumerate(self.parsed_items["INS"]):
            try:
                self.new["modes"]\
                        ["instantaneous"]\
                        ["sources"]\
                        [f"source_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                    "mass": float(item[3]),
                    "time": float(item[4])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("INS", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("INS", self.ord(idx), 5)

    def add_INF(self):
        for idx, item in enumerate(self.parsed_items["INF"]):
            try:
                self.new["modes"]\
                        ["infinite_duration"]\
                        ["sources"]\
                        [f"source_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                    "rate": float(item[3]),
                    "time": float(item[4])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("INF", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("INF", self.ord(idx), 5)

    def add_FIX(self):
        for idx, item in enumerate(self.parsed_items["FIX"]):
            try:
                self.new["modes"]\
                        ["fixed_duration"]\
                        ["sources"]\
                        [f"source_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                    "rate": float(item[3]),
                    "start_time": float(item[4]),
                    "end_time": float(item[5])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("FIX", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("FIX", self.ord(idx), 6)
    
    def add_POI(self):
        for idx, item in enumerate(self.parsed_items["POI"]):
            try:
                self.new["models"]\
                        ["eddy_diffusion"]\
                        ["monitor_locations"]\
                        ["points"]\
                        [f"point_{idx}"] = {
                    "x": float(item[0]),
                    "y": float(item[1]),
                    "z": float(item[2]),
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("POI", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("POI", self.ord(idx), 3)
 
    
    def add_LIN(self):
        for idx, item in enumerate(self.parsed_items["LIN"]):
            try:
                self.new["models"]\
                        ["eddy_diffusion"]\
                        ["monitor_locations"]\
                        ["lines"]\
                        [f"line_{idx}"] = {
                    "pointA": {
                        "x": float(item[0]),
                        "y": float(item[1]),
                        "z": float(item[2]),
                    },
                    "pointB": {
                        "x": float(item[3]),
                        "y": float(item[4]),
                        "z": float(item[5]),
                    }
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("LIN", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("LIN", self.ord(idx), 6)

    
    def add_PLA(self):
        for idx, item in enumerate(self.parsed_items["PLA"]):
            try:
                self.new["models"]\
                        ["eddy_diffusion"]\
                        ["monitor_locations"]\
                        ["planes"]\
                        [f"plane_{idx}"] = {
                    "axis": str(item[0]),
                    "distance": float(item[1])
                }
            except ValueError as e:
                raise CSVToConfigFileValueError("PLA", self.ord(idx))
            except IndexError as e:
                raise CSVToConfigFileIndexError("PLA", self.ord(idx), 2)
    
    def write_new_config_file(self):
        if not self.output_file_path:
            with open(self.append_id(self.config_file_path), 'w') as f:
                f.write(json.dumps(self.new, indent=4))
        else:
            with open(self.output_file_path, 'w') as f:
                f.write(json.dumps(self.new, indent=4))
            

    def ord(self, n):
        return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}\
            .get(n%10, "th"))

    def append_id(self, filename):
        return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + ["new"]) 

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CSVToConfigFileOSError(Error):
    """The exception raised when a :class:`~.CSVToConfigFile` instance
    catches an error when parsing a csv file path.

    """
    def __init__(self, path: str, error: OSError):
        """The constructor for the :class:`CSVToConfigFileOSError` class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}"
        super().__init__(msg)


class CSVToConfigFileValueError(Error):
    """The exception raised when a :class:`~.CSVToConfigFile` instance
    catches a ValueError error when parsing a csv file.

    """
    def __init__(self, category: str, index: int):
        """The constructor for the :class:`CSVToConfigFileValueError` class.

        """
        msg = f"While loading the {index} {category} item, one of the parsed "\
              f"items was of an incorrect type."
        super().__init__(msg)


class CSVToConfigFileIndexError(Error):
    """The exception raised when a :class:`~.CSVToConfigFile` instance
    catches an IndexError error when parsing a csv file.

    """
    def __init__(self, category: str, index: str, expected: int):
        """The constructor for the :class:`CSVToConfigFileIndexError` class.

        """
        msg = f"While loading the {index} {category} item, not enough "\
              f"values were found. Expecting {expected}"
        super().__init__(msg)
