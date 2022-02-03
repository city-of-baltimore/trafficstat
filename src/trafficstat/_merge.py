"""Helper that makes up for the lack of MERGE in SqlAlchemy. One day they will support that, and this can be removed"""
from loguru import logger
from sqlalchemy import engine as engine_type, inspect as sqlalchemyinspect  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.orm.decl_api import DeclarativeMeta  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from sqlalchemy.sql import text  # type: ignore


def insert_or_update(insert_obj: DeclarativeMeta, engine: engine_type, identity_insert=False) -> None:
    """
    A safe way for the sqlalchemy to insert if the record doesn't exist, or update if it does. Copied from
    trafficstat.crash_data_ingester
    :param insert_obj: `sqlalchemy.ext.declarative.DeclarativeMeta` to insert into the database
    :param engine: the sqlalchemy engine to use to insert
    :param identity_insert: Used internally when we try to insert and will have to update instead.
    """
    session = Session(bind=engine, future=True)
    if identity_insert:
        session.execute(text(f'SET IDENTITY_INSERT {insert_obj.__tablename__} ON'))

    session.add(insert_obj)
    try:
        session.commit()
        logger.debug('Successfully inserted object: {}', insert_obj)
    except IntegrityError as insert_err:
        session.rollback()

        if '(544)' in insert_err.args[0]:
            # This is a workaround for an issue with sqlalchemy not properly setting IDENTITY_INSERT on for SQL
            # Server before we insert values in the primary key. The error is:
            # (pyodbc.IntegrityError) ('23000', "[23000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
            # Cannot insert explicit value for identity column in table <table name> when IDENTITY_INSERT is set to
            # OFF. (544) (SQLExecDirectW)")
            insert_or_update(insert_obj, engine, True)

        elif '(2627)' in insert_err.args[0] or 'UNIQUE constraint failed' in insert_err.args[0]:
            # Error 2627 is the Sql Server error for inserting when the primary key already exists. 'UNIQUE
            # constraint failed' is the same for Sqlite
            cls_type = type(insert_obj)

            qry = session.query(cls_type)

            primary_keys = [i.key for i in sqlalchemyinspect(cls_type).primary_key]
            for primary_key in primary_keys:
                qry = qry.filter(cls_type.__dict__[primary_key] == insert_obj.__dict__[primary_key])

            update_vals = {k: v for k, v in insert_obj.__dict__.items()
                           if not k.startswith('_') and k not in primary_keys}
            if update_vals:
                qry.update(update_vals)
                try:
                    session.commit()
                    logger.debug('Successfully inserted object: {}', insert_obj)
                except IntegrityError as update_err:
                    logger.error('Unable to insert object: {}\nError: {}', insert_obj, update_err)

        else:
            raise AssertionError(f'Expected error 2627 or "UNIQUE constraint failed". Got {insert_err}') \
                from insert_err
    finally:
        if identity_insert:
            session.execute(text(f'SET IDENTITY_INSERT {insert_obj.__tablename__} OFF'))
        session.close()
