from hma_backend import db


class MetabolicModel(db.Model):
    __tablename__ = "metabolic_model"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name):
        self.name = name

