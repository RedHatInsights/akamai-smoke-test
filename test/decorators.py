from urllib3.util import connection
_orig_create_connection = connection.create_connection
def modify_ip(ip):
    def decorator(func):
        def wrapper(data_element):
            def my_create_connection(address, *args, **kwargs):
                host, port = address
                return _orig_create_connection((ip, port), *args, **kwargs)
            connection.create_connection = my_create_connection
            func(data_element)
            connection.create_connection = _orig_create_connection
        return wrapper
    return decorator
