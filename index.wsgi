import sae
from dianfei import wsgi

application = sae.create_wsgi_app(wsgi.application)
