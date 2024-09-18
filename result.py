from enum import IntEnum

class Result(IntEnum):
    NO_BOTTLE = 0
    ACCEPT = 1
    INSPECT = 2
    REJECT = 3

def combine_results(results: list[Result]) -> Result:
    return max(results)