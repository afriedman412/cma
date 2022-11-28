"""
These were created mostly to help unravel some debugging issues but should probably be built out more thoroughly.
"""

class EncodingError(Exception):
    pass

class DecodingError(Exception):
    pass

class TrackPathException(Exception):
    pass

class LabelTypeError(Exception):
    pass