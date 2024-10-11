from . import db
from datetime import datetime

class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo_de_obra = db.Column(db.Integer, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_prevista_termino = db.Column(db.Date, nullable=True)
    data_termino = db.Column(db.Date, nullable=True)
    concluida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    fotos = db.relationship('Foto', backref='obra', lazy=True)

class Foto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    foto = db.Column(db.LargeBinary, nullable=False)
    tipo = db.Column(db.Integer, nullable=False)  # 0 = landscape, 1 = portrait, 2 = square
    obra_id = db.Column(db.Integer, db.ForeignKey('obra.id'), nullable=False)
