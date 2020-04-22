

class EddyDiffusion:

    def __init__(self, settings):
        pass

    def __call__(self, x, y, z, t, n):
        # calls one of the ther computational methods depending on selected mode.
        return float

    def __instanteneous(self, x, y, z, t, n):
        return float
    
    def __infinite(self, x, y, z, t, n):
        return float
    
    def __fixed(self, x, y, z, t, n):
        return float
    
    def __coeff(self, t):
        # Compute time dependent cofefficient.
        return float

    def __image(self, axis, x, y, z, t, n):
        # Compute the image term on a given axis.
        return float
    
    def __concentration(self, x, y, z, t):
        # uses __coeff and __image  and settings to compute the concentration
        # at  a given time and place.
        return float
