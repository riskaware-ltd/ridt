from config import IDMFConfig


class ThresholdResults:
    def __init__(self, number_of_thresholds: int):
        if not isinstance(number_of_thresholds, int):
            raise ValueError("Expecting integer.")
        self.points = [DomainResults() for i in range(number_of_thresholds)]
        self.lines = [DomainResults() for i in range(number_of_thresholds)]
        self.planes = [DomainResults() for i in range(number_of_thresholds)]
        self.domain = [DomainResults() for i in range(number_of_thresholds)]


class MaximumResults:
    def __init__(self):
        self.points = DomainResults()
        self.lines = DomainResults()
        self.planes = DomainResults()
        self.domain = DomainResults()

class DomainResults:

    def __init__(self):
        self.anywhere = None
        self.percentage = None
        self.maximum = None
