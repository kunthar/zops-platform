from falcon.errors import HTTPInternalServerError, HTTPConflict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from zopsm.saas.config import SQLALCHEMY_DATABASE_URI
from zopsm.saas.database import ResourceDB
from sqlalchemy.exc import IntegrityError
from zopsm.saas.log_handler import saas_logger

session_factory = sessionmaker(bind=create_engine(SQLALCHEMY_DATABASE_URI))
Session = scoped_session(session_factory)


class DatabaseSessionManager(object):

    def __init__(self):
        self.session = Session()
        self.db = ResourceDB(self.session)

    def process_resource(self, req, resp, resource, params):
        resource.db = self.db

    def process_response(self, req, resp, resource, req_succeeded):
        if req_succeeded:
            try:
                self.db.session.commit()
            except IntegrityError as e:
                self.db.session.rollback()
                saas_logger.error(e)
                raise HTTPConflict(description="There is an conflict please change input value")
            except Exception as e:
                self.db.session.rollback()
                saas_logger.error(e)
                raise HTTPInternalServerError(description="Critical error occurred. We handle this error as soon as "
                                                          "possible time")
        else:
            self.db.session.rollback()
        Session.remove()
