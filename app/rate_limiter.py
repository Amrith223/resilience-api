from slowapi import Limiter
from slowapi.util import get_remote_address

# get_remote_address reads the client's IP address from the request
# Each IP gets its own separate counter
limiter = Limiter(key_func=get_remote_address)