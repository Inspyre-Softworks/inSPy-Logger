class ByteConverter:
    """
    A class to convert between various units of digital storage.

    Supported units: Bytes, Kilobytes, Megabytes, Gigabytes, Terabytes, Petabytes, Exabytes, Zettabytes, Yottabytes,
                     Kibibytes, Mebibytes, Gibibytes, Tebibytes, Pebibytes, Exbibytes, Zebibytes, Yobibytes.

    Methods:
        convert(value, from_unit, to_unit): Converts the given value from one unit to another.
    """

    # Dictionary to store conversion rates relative to bytes
    _conversion_rates = {
        'bytes': 1,
        'kilobytes':  1000,
        'megabytes':  1000 ** 2,
        'gigabytes':  1000 ** 3,
        'terabytes':  1000 ** 4,
        'petabytes':  1000 ** 5,
        'exabytes':   1000 ** 6,
        'zettabytes': 1000 ** 7,
        'yottabytes': 1000 ** 8,
        'kibibytes':  1024,
        'mebibytes':  1024 ** 2,
        'gibibytes':  1024 ** 3,
        'tebibytes':  1024 ** 4,
        'pebibytes':  1024 ** 5,
        'exbibytes':  1024 ** 6,
        'zebibytes':  1024 ** 7,
        'yobibytes':  1024 ** 8
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        """
        Converts the given value from one unit to another.

        Parameters:
            value (float): The value to convert.
            from_unit (str): The unit to convert from. Must be one of the supported units.
            to_unit (str): The unit to convert to. Must be one of the supported units.

        Returns:
            float: The converted value in the target unit.

        Raises:
            ValueError: If an unsupported unit is specified.
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit not in cls._conversion_rates or to_unit not in cls._conversion_rates:
            raise ValueError("Unsupported unit. Supported units are: " + ', '.join(cls._conversion_rates.keys()))

        # Convert the value to bytes first, then to the target unit
        value_in_bytes = value * cls._conversion_rates[from_unit]
        return value_in_bytes / cls._conversion_rates[to_unit]
