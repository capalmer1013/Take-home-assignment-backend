from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

import uuid

db = SQLAlchemy()


class BaseMixin(object):
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # Makes sure the columns are added to the end of the table
    created_at._creation_order = 9998
    updated_at._creation_order = 9999

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def deleteOne(cls, **kw):
        obj = cls.query.filter_by(**kw).first()
        if obj:
            db.session.delete(obj)
            db.session.commit()


class User_Account(BaseMixin, db.Model):
    __tablename__ = "user_account"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    user_name = db.Column(db.String())

    def __repr__(self):
        return "<User_Account %r>" % self.__dict__


class Data_Stream(BaseMixin, db.Model):
    __tablename__ = "data_stream"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    key = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
