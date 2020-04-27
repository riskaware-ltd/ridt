from config.ConfigFileParser import ConfigFileParser
from config.idmfconfig import IDMFConfig

import numpy as np


class WellMixed:

    def __init__(self):
        pass

    def __call__(self, settings: IDMFConfig, time_array: np.ndarray):
        """try:
            return getattr(self, f"__{self.settings.release_type}")(settings, time_array)
        except AttributeError as e:
            raise e"""

        if settings.release_type == "instantaneous":
            return self.__instantaneous(settings, time_array)

        if settings.release_type == "fixed_duration":
            return self.__fixed(settings, time_array)

        if settings.release_type == "infinite_duration":
            return self.__infinite(settings, time_array)

    def __instantaneous(self, settings: IDMFConfig, time_array: np.ndarray):
        sources = settings.modes.instantaneous.sources
        concentration = []
        for source_name, source in sources.items():
            concentration.append(self.__instantaneous_concentration(
                settings, source, time_array))
        return [sum(x) for x in zip(*concentration)]

    @staticmethod
    def __instantaneous_concentration(settings, source, time_array: np.ndarray):
        volume = settings.models.well_mixed.volume
        fa_rate = settings.fresh_air_change_rate
        concentration = []
        for time in time_array:
            if time < source.time:
                concentration.append(0)
            if time >= source.time:
                concentration.append(
                    (source.mass / volume) * np.exp(
                        -(fa_rate / volume) * (time - source.time))
                )
        return concentration

    def __infinite(self, settings: IDMFConfig, time_array: np.ndarray):
        sources = settings.modes.infinite_duration.sources
        concentration = []
        for source_name, source in sources.items():
            concentration.append(self.__infinite_concentration(
                settings, source, time_array))
        return [sum(x) for x in zip(*concentration)]

    @staticmethod
    def __infinite_concentration(settings, source, time_array: np.ndarray):
        volume = settings.models.well_mixed.volume
        fa_rate = settings.fresh_air_change_rate
        concentration = []
        for time in time_array:
            if time < source.time:
                concentration.append(0)
            if time >= source.time:
                concentration.append(
                    (source.rate / fa_rate) * (1 - np.exp(
                        -(fa_rate / volume) * (time - source.time)))
                )
        return concentration

    def __fixed(self, settings: IDMFConfig, time_array: np.ndarray):
        sources = settings.modes.fixed_duration.sources
        concentration = []
        for source_name, source in sources.items():
            concentration.append(self.__fixed_concentration(
                settings, source, time_array))
        return [sum(x) for x in zip(*concentration)]

    @staticmethod
    def __fixed_concentration(settings, source, time_array: np.ndarray):
        volume = settings.models.well_mixed.volume
        fa_rate = settings.fresh_air_change_rate
        concentration = []
        for time in time_array:
            if time < source.start_time:
                concentration.append(0)
            if source.start_time <= time <= source.end_time:
                concentration.append(
                    (source.rate / fa_rate) * (1 - np.exp(
                        -(fa_rate / volume) * (time - source.start_time)))
                )
            if time > source.end_time:
                if concentration[-1] >= concentration[-2]:
                    c_end = concentration[-1]
                    end_index = concentration.index(c_end)
                    t_end = time_array[end_index]
                concentration.append(
                    c_end * np.exp(
                        -(fa_rate / volume) * ((time - source.start_time) - t_end)
                    )
                )
        return concentration


c = ConfigFileParser()
config = c("../default/config.json")

w = WellMixed()
y = w(config, np.array(range(100)))

import matplotlib.pyplot as plt

plt.plot(range(0, 100, 1), y)
plt.xlabel("Time")
plt.ylabel("Concentration")
plt.title("Well Mixed Instantaneous release with two sources.")
plt.show()
