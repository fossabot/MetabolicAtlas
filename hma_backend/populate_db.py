from hma_backend import db

from hma_backend.models import MetabolicModel


dummy = MetabolicModel("dummy")

db.session.add(dummy)
db.session.commit()
