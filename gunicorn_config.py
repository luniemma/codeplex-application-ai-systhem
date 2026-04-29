"""
Gunicorn Configuration
"""
import multiprocessing
import os

# Server socket
bind = os.getenv('API_HOST', '0.0.0.0') + ':' + str(os.getenv('API_PORT', 8000))
backlog = 2048

# Worker processes
workers = int(os.getenv('API_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = os.getenv('ACCESS_LOG', 'logs/access.log')
errorlog = os.getenv('ERROR_LOG', 'logs/error.log')
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'codeplex-ai'

# Server mechanicsgs
daemon = False
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = os.getenv('SSL_KEY', None)
certfile = os.getenv('SSL_CERT', None)
ssl_version = 'TLSv1_2'

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized"""
    print('Codeplex AI Gunicorn server is starting...')

def on_exit(server):
    """Called just after the server is halted"""
    print('Codeplex AI Gunicorn server has exited')

def worker_int(worker):
    """Called when a worker receives the SIGINT signal"""
    print(f'Worker {worker.pid} received SIGINT')

def worker_abort(worker):
    """Called when a worker is aborted"""
    print(f'Worker {worker.pid} has been aborted')

