from .idmfconfig import IDMFConfig

def summary(settings: IDMFConfig):
    rv = str()

    rv += f"Models:\n"
    rv += f"\tEddy Diffusion: {settings.eddy_diffusion}\n"
    rv += f"\tWell Mixed: {settings.well_mixed}\n"
    rv += f"\n"

    rv += f"total time: {settings.total_time}{settings.time_units}\n"
    rv += f"fresh air change rate: {settings.fresh_air_change_rate}{settings.fresh_air_change_rate_units}\n"
    rv += f"\n"

    if settings.eddy_diffusion:
        rv += f"spatial_dimensions:\n"
        rv += f"\tx: {settings.models.eddy_diffusion.dimensions.x}\n"
        rv += f"\ty: {settings.models.eddy_diffusion.dimensions.y}\n"
        rv += f"\tz: {settings.models.eddy_diffusion.dimensions.z}\n"
        coeff = settings.models.eddy_diffusion.coefficient
        rv += f"\n"
        if coeff.calculation == "TKEB":
            rv += f"diffusion coefficient: TKEB\n"
            rv += f"\tvents: {coeff.tkeb.number_of_supply_vents}\n"
            rv += f"\ttotal air change rate: {coeff.tkeb.total_air_change_rate}\n"
        else:
            rv += f"diffusion coefficient: {coeff.value}\n"
        rv += f"\n"
    if settings.well_mixed:
        rv += f"well mixed volume: {settings.models.well_mixed.volume} m3\n"
        rv += f"\n"

    rv += "sources\n"
    rv += "-------\n"

    rv += "instantaneous:\n"
    for name, item in settings.modes.instantaneous.sources.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x}\n"
        rv += f"\t\ty: {item.y}\n"
        rv += f"\t\tz: {item.z}\n"
        rv += f"\t\tmass: {item.mass}\n"
        rv += f"\t\ttime: {item.time}\n"
        rv += f"\n"
    rv += "infinite duration:\n"
    for name, item in settings.modes.infinite_duration.sources.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x}\n"
        rv += f"\t\ty: {item.y}\n"
        rv += f"\t\tz: {item.z}\n"
        rv += f"\t\trate: {item.rate}\n"
        rv += f"\t\ttime: {item.time}\n"
        rv += f"\n"
    rv += "infinite duration:\n"
    for name, item in settings.modes.fixed_duration.sources.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x}\n"
        rv += f"\t\ty: {item.y}\n"
        rv += f"\t\tz: {item.z}\n"
        rv += f"\t\trate: {item.rate}\n"
        rv += f"\t\tstart_time: {item.end_time}\n"
        rv += f"\t\tend_time: {item.end_time}\n"
        rv += f"\n"
    
    rv += "\n"
    rv += "monitor locations\n"
    rv += "-----------------\n"

    rv += "points:\n"
    for name, item in settings.models.eddy_diffusion.monitor_locations.points.items():
        rv += f"\t{name}\n"
        rv += f"\t\tx: {item.x}\n"
        rv += f"\t\ty: {item.y}\n"
        rv += f"\t\tz: {item.z}\n"
        rv += f"\n"
    
    rv += "lines:\n"
    for name, item in settings.models.eddy_diffusion.monitor_locations.lines.items():
        rv += f"\t{name}\n"
        rv += f"\t\tpoint - x: {item.point.x}\n"
        rv += f"\t\tpoint - y: {item.point.y}\n"
        rv += f"\t\tpoint - z: {item.point.z}\n"
        rv += f"\t\tparallel axis: {item.parallel_axis}\n"
        rv += f"\n"
    
    rv += "planes:\n"
    for name, item in settings.models.eddy_diffusion.monitor_locations.planes.items():
        rv += f"\t{name}\n"
        rv += f"\t\tplane: {item.axis}\n"
        rv += f"\t\tposition: {item.distance}\n"
        rv += f"\n"

    return rv