import sys
import json


if __name__ == '__main__':

    n = {
        "agent_molecular_weight_units": "mol.m-3",
        "agent_molecular_weight": 1.0,
        "pressure_units": "Pa",
        "pressure": 1.0,
        "temperature_units": "K",
        "temperature": 273.0
    }
    path = sys.argv[1]
    with open(path, 'r') as f:
        d = json.loads(f.read())
    
    d["spatial_samples"] = d["models"]["eddy_diffusion"]["spatial_samples"]
    del d["models"]["eddy_diffusion"]["spatial_samples"]

    
    d["dimensions"] = d["models"]["eddy_diffusion"]["dimensions"]
    del d["models"]["eddy_diffusion"]["dimensions"]

    d["physical_properties"] = n

    del d["models"]["well_mixed"]

    with open(path, 'w') as f:
        f.write(json.dumps(d, indent=4))
    print(print(d))