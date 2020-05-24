from .idmfconfig import IDMFConfig

def summary(settings: IDMFConfig):
    rv = str()

    rv += f"dispersion model: {settings.dispersion_model}\n"
    rv += f"time units: {settings.time_units}\n"
    rv += f"total time: {settings.total_time}\n"

    rv += f"concentration units: {settings.concentration_units}\n"
    rv += f"exposure units: {settings.exposure_units}\n"

    rv += f"total air change rate: {settings.total_air_change_rate}\n"
    rv += f"fresh air change rate: {settings.fresh_air_change_rate}\n"


    if settings.dispersion_model == "eddy_diffusion":
        rv += f"spatial_units: {settings.models.eddy_diffusion.spatial_units}\n"
        rv += f"spatial_dimensions: "
        rv += f"x: {settings.models.eddy_diffusion.dimensions.x}, "
        rv += f"y: {settings.models.eddy_diffusion.dimensions.y}, "
        rv += f"z: {settings.models.eddy_diffusion.dimensions.z}\n"
        coeff = settings.models.eddy_diffusion.coefficient
        if coeff.calculation == "TKEB":
            rv += f"diffusion coefficient: TKEB "
            rv += f"(vents: {coeff.tkeb.number_of_supply_vents})\n"
        else:
            rv += f"diffusion coefficient: {coeff.value}\n"
    else:
        rv += f"volume: {settings.models.well_mixed.volume}"

    rv += "\n"
    rv += "sources\n"
    rv += "-------\n"
    rv += "instantaneous:\n"

    for name, item in settings.modes.instantaneous.sources.items():
        rv += f"\t{name}, "
        if settings.dispersion_model == "eddy_diffusion":
            rv += f"x: {item.x}, "
            rv += f"y: {item.y}, "
            rv += f"z: {item.z}, "
        rv += f"mass: {item.mass}, "
        rv += f"time: {item.time}"
        rv += f"\n"
    rv += "infinite duration:\n"
    for name, item in settings.modes.infinite_duration.sources.items():
        rv += f"\t{name}, "
        if settings.dispersion_model == "eddy_diffusion":
            rv += f"x: {item.x}, "
            rv += f"y: {item.y}, "
            rv += f"z: {item.z}, "
        rv += f"rate: {item.rate}, "
        rv += f"time: {item.time}"
        rv += f"\n"
    rv += "infinite duration:\n"
    for name, item in settings.modes.fixed_duration.sources.items():
        rv += f"\t{name}, "
        if settings.dispersion_model == "eddy_diffusion":
            rv += f"x: {item.x}, "
            rv += f"y: {item.y}, "
            rv += f"z: {item.z}, "
        rv += f"rate: {item.rate}, "
        rv += f"start_time: {item.end_time}, "
        rv += f"end_time: {item.end_time}"
        rv += f"\n"


    return rv