# Configuração do Gunicorn para a aplicação RAG
# Arquivo: gunicorn.conf.py

# Configurações do servidor
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Configurações de timeout
timeout = 120
keepalive = 5

# Configurações de log
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Configurações de processo
daemon = False
pidfile = "logs/gunicorn.pid"
user = None
group = None

# Configurações de desenvolvimento
reload = False
preload_app = True

# Configurações de segurança
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
