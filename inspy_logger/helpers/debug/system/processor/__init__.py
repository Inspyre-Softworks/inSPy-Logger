import platform
import multiprocessing
import psutil


# Function to check if the system architecture is 64-bit
def is_64bit():
    """
    Checks if the system architecture is 64-bit.

    Returns:
        bool: True if the system architecture is 64-bit, False otherwise.
    """
    return platform.architecture()[0] == '64bit'


# Function to get the number of cores
def number_of_cores():
    """
    Gets the number of cores in the system.

    Returns:
        int: The number of cores in the system.
    """
    return multiprocessing.cpu_count()


# Function to get the processor core information
def get_processor_core_info():
    """
    Gets the processor core information.

    Returns:
        dict: A dictionary containing the total number of cores, the number of physical cores, and the number of logical cores.
    """
    phys = psutil.cpu_count(logical=False)
    total = number_of_cores()

    return {
        'total': total,
        'physical': phys,
        'logical': total - phys
    }


# Function to get the processor information
def _get_processor_info():
    """
    Gets the processor information.

    Returns:
        dict: A dictionary containing the name of the processor, the architecture of the processor, and the core information of the processor.
    """
    cores = get_processor_core_info()

    return {
        'name': platform.processor(),
        'architecture': '64-bit' if is_64bit() else '32-bit',
        'cores': get_processor_core_info()
    }


# A dictionary containing the processor information
PROCESSOR_INFO = _get_processor_info()
