from config.idmfconfig import IDMFConfig

import numpy as np


class WellMixed:

    def __init__(self):
        pass

    def __call__(self, settings: IDMFConfig, time_array: np.ndarray):
        try:
            return getattr(self, f"_{settings.release_type}")(settings, time_array)
        except AttributeError:
            f"Release type must be instantaneous, fixed_duration or infinite_duration"

    def _instantaneous(self, settings: IDMFConfig, time_array: np.ndarray):
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

    def _infinite_duration(self, settings: IDMFConfig, time_array: np.ndarray):
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

    def _fixed_duration(self, settings: IDMFConfig, time_array: np.ndarray):
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
        for index, time in enumerate(time_array):
            if time < source.start_time:
                concentration.append(0)
            if source.start_time <= time <= source.end_time:
                concentration.append(
                    (source.rate / fa_rate) * (1 - np.exp(
                        -(fa_rate / volume) * (time - source.start_time)))
                )
            if time > source.end_time:
                concentration.append(
                    concentration[int(source.end_time) - 1] * np.exp(
                        -(fa_rate / volume) * (time - source.end_time)
                    )
                )
        return concentration
