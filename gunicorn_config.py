# Gunicorn configuration file
# Use this configuration for production deployment

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 2  # Number of worker processes
worker_class = "uvicorn.workers.UvicornWorker"  # Use uvicorn worker for FastAPI
worker_connections = 1000  # Maximum number of simultaneous connections per worker
timeout = 1800  # Workers silent for more than this many seconds are killed and restarted (30 minutes)
keepalive = 5  # The number of seconds to wait for requests on a Keep-Alive connection
max_requests = 1000  # Restart workers after this many requests
max_requests_jitter = 100  # Jitter for max_requests

# Logging
accesslog = "-"  # Log access to stdout
errorlog = "-"   # Log errors to stdout
loglevel = "info"  # Level of messages to output
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'jsi-scraper'

# Server mechanics
preload_app = True  # Preload application code before forking workers
daemon = False      # Don't run as daemon