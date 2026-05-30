from app.main import app as myfastapp
from a2wsgi import ASGIMiddleware

fastapiapp = ASGIMiddleware(app=myfastapp)
