from flask import jsonify

from hma_backend import app
from hma_backend.models import MetabolicModel

@app.route("/")
def index():
    model = MetabolicModel.query.order_by(MetabolicModel.name.desc()).first()
    return jsonify(id=model.id, name=model.name)

