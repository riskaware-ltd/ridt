from typing import Iterable

from .ridtconfig import RIDTConfig
from .units import Units
from ridt.equation.eddy_diffusion import EddyDiffusion


def summary(settings: RIDTConfig) -> str:
    """A function that generates a formatted string containing run info.

    This takes a settings object and generates a string with various information
    about the run. It also computes various sanity check quantities.

    Parameters
    ----------
    settings : :class:`~.RIDTConfig`
        The settings object for the run in question. 

    Returns
    -------
    :obj:`str` 
        The formatted string, ready to be written to a file.
    """
    units = Units(settings)
    rv = str()
    rv += f"RIDT v1.0\n"

    rv += f"Models:\n"
    rv += f"\tEddy Diffusion: {settings.eddy_diffusion}\n"
    rv += f"\tWell Mixed: {settings.well_mixed}\n"
    rv += f"\n"

    rv += f"total time: {settings.total_time} {settings.time_units}\n"
    rv += f"\n"
    rv += f"spatial_dimensions:\n"
    rv += f"\tx: {settings.dimensions.x} {units.space}\n"
    rv += f"\ty: {settings.dimensions.y} {units.space}\n"
    rv += f"\tz: {settings.dimensions.z} {units.space}\n"
    rv += f"\n"
    rv += f"fresh air change rate: {settings.fresh_air_flow_rate} {settings.fresh_air_flow_rate_units}\n"
    rv += f"\n"

    if settings.eddy_diffusion:
        coeff = settings.models.eddy_diffusion.coefficient
        rv += f"\n"
        if coeff.calculation == "TKEB":
            rv += f"diffusion coefficient: TKEB\n"
            rv += f"\tvents: {coeff.tkeb.number_of_supply_vents}\n"
            rv += f"\ttotal air change rate: {coeff.tkeb.total_air_flow_rate} m3.s-1\n"
            M = EddyDiffusion(settings)
            rv += f"diffusion coefficient value: {M.diffusion_coefficient()} m2.s-1\n"
        else:
            rv += f"diffusion coefficient value: {coeff.value} m2.s-1\n"
        if settings.models.eddy_diffusion.images.mode == "manual":
            rv += f"number of image sources computed (either side of zero): \
                {settings.models.eddy_diffusion.images.quantity}"
        else:
            rv += f"number of image sources computed: auto."
        rv += f"\n"
    if settings.well_mixed:
        dim = settings.dimensions
        if isinstance(dim.x, list) or isinstance(dim.y, list) or isinstance(dim.z, list):
            rv += f"well mixed volume: <various> m3\n"
        else:
            rv += f"well mixed volume: {settings.dimensions.x * settings.dimensions.y *  settings.dimensions.z} m3\n"
        rv += f"\n"

    rv += "sources\n"
    rv += "-------\n"

    rv += "instantaneous:\n"
    for name, item in settings.modes.instantaneous.sources.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x} {units.space}\n"
        rv += f"\t\ty: {item.y} {units.space}\n"
        rv += f"\t\tz: {item.z} {units.space}\n"
        rv += f"\t\tmass: {item.mass} {units.mass}\n"
        rv += f"\t\ttime: {item.time} {units.time}\n"
        dim = settings.dimensions
        if isinstance(item.mass, list) or\
           isinstance(dim.x, list) or\
           isinstance(dim.y, list) or\
           isinstance(dim.z, list):
            rv += f"\t\tsteady state well mix concentration: <various>\n"
        else:
            vol = settings.dimensions.x * settings.dimensions.y * settings.dimensions.z
            rv += f"\t\tsteady state well mix concentration: {(item.mass / vol):.2e} {units.concentration_si}\n"
        if isinstance(item.mass, list) or\
           isinstance(settings.fresh_air_flow_rate, list):
            rv += f"\t\tupper exposure limit: <various>\n"
        else:
            if settings.fresh_air_flow_rate:
                rv += f"\t\tupper exposure limit: \
                    {(item.mass / settings.fresh_air_flow_rate):.2e} {units.exposure_si}\n"
            else:
                rv += f"\t\tupper exposure limit: infinite.\n"


        rv += f"\n"
    rv += "infinite duration:\n"
    for name, item in settings.modes.infinite_duration.sources.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x} {units.space}\n"
        rv += f"\t\ty: {item.y} {units.space}\n"
        rv += f"\t\tz: {item.z} {units.space}\n"
        rv += f"\t\trate: {item.rate} kg.m-3\n"
        rv += f"\t\ttime: {item.time} {units.time}\n"
        if isinstance(item.rate, list) or\
           isinstance(settings.fresh_air_flow_rate, list):
            rv += f"\t\tsteady state well mix concentration: <various>\n"
        else:
            if settings.fresh_air_flow_rate:
                rv += f"\t\tsteady state well mix concentration: \
                    {(item.rate / settings.fresh_air_flow_rate):.2e} {units.concentration_si}\n"
            else:
                rv += f"\t\tsteady state well mix concentration: infinite\n"

        rv += f"\n"
    rv += "fixed duration:\n"
    for name, item in settings.modes.fixed_duration.sources.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x} {units.space}\n"
        rv += f"\t\ty: {item.y} {units.space}\n"
        rv += f"\t\tz: {item.z} {units.space}\n"
        rv += f"\t\trate: {item.rate} kg.m-3\n"
        rv += f"\t\tstart_time: {item.end_time} {units.time}\n"
        rv += f"\t\tend_time: {item.end_time} {units.time}\n"
        dim = settings.dimensions
        if isinstance(item.rate, list) or\
           isinstance(dim.x, list) or\
           isinstance(dim.y, list) or\
           isinstance(dim.z, list) or\
           isinstance(item.start_time, list) or\
           isinstance(item.end_time, list):
            rv += f"\t\tsteady state well mix concentration: <various>\n"
        else:
            vol = settings.dimensions.x * settings.dimensions.y * settings.dimensions.z
            rv += f"\t\tsteady state well mix concentration: \
                {(item.rate * (item.end_time - item.end_time) / vol):.2e} {units.concentration_si}\n"
        if isinstance(item.rate, list) or\
           isinstance(item.start_time, list) or\
           isinstance(item.end_time, list) or\
           isinstance(settings.fresh_air_flow_rate, list):
            rv += f"\t\tupper exposure limit: <various>\n"
        else:
            if settings.fresh_air_flow_rate:
                rv += f"\t\tupper exposure limit: \
                    {(item.rate * (item.end_time - item.end_time) / settings.fresh_air_flow_rate):.2e} {units.exposure_si}\n"
            else:
                rv += f"\t\tupper exposure limit: infinite\n"

        rv += f"\n"
    
    rv += "\n"
    rv += "monitor locations\n"
    rv += "-----------------\n"

    rv += "points:\n"
    for name, item in settings.models.eddy_diffusion.monitor_locations.points.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x} {units.space}\n"
        rv += f"\t\ty: {item.y} {units.space}\n"
        rv += f"\t\tz: {item.z} {units.space}\n"
        rv += f"\n"
    
    rv += "lines:\n"
    for name, item in settings.models.eddy_diffusion.monitor_locations.lines.items():
        rv += f"\t{name}\n"
        rv += f"\t\tpoint - x: {item.point.x} {units.space}\n"
        rv += f"\t\tpoint - y: {item.point.y} {units.space}\n"
        rv += f"\t\tpoint - z: {item.point.z} {units.space}\n"
        rv += f"\t\tparallel axis: {item.parallel_axis}\n"
        rv += f"\n"
    
    rv += "planes:\n"
    for name, item in settings.models.eddy_diffusion.monitor_locations.planes.items():
        rv += f"\t{name}\n"
        rv += f"\t\tplane: {item.axis}\n"
        rv += f"\t\tposition: {item.distance} {units.space}\n"
        rv += f"\n"

    return rv