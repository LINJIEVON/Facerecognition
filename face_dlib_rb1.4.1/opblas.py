#
#	refrence link： https://stackoverflow.com/questions/29559338/set-max-number-of-threads-at-runtime-on-numpy-openblas
#
import ctypes
from ctypes.util import find_library

# Prioritize hand-compiled OpenBLAS library over version in /usr/lib/
# from Ubuntu repos
try_paths = ['/usr/lib/libopenblas.so.0',
	    '/usr/lib/libopenblas.so',
	    '/lib/libopenblas.so',
             find_library('openblas')]
openblas_lib = None
for libpath in try_paths:
    try:
        openblas_lib = ctypes.cdll.LoadLibrary(libpath)
        break
    except OSError:
        continue
if openblas_lib is None:
    raise EnvironmentError('Could not locate an OpenBLAS shared library', 2)


def set_num_threads(n):
    """Set the current number of threads used by the OpenBLAS server."""
    openblas_lib.openblas_set_num_threads(int(n))


if __name__ == "__main__": 
    pass
	
	

	
