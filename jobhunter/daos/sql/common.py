import os
from typing import Any, Callable, Iterable, Tuple

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

import jobhunter.config
from jobhunter.daos import common

if hasattr(jobhunter.config, "SQL_FILENAME"):
    SQLITE_PATH = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), jobhunter.config.SQL_FILENAME)
    SQLALCHEMY_ENGINE = sqlalchemy.create_engine(SQLITE_PATH)
else:
    SQLALCHEMY_ENGINE = sqlalchemy.create_engine(jobhunter.config.SQL_URL)

METADATA = sqlalchemy.MetaData(SQLALCHEMY_ENGINE)

Base = declarative_base()
Session = sessionmaker(bind=SQLALCHEMY_ENGINE)
ComparisonFunc = Callable[[common.T], BinaryExpression]
Filter = Tuple[common.Filterable[common.T], ComparisonFunc[common.T]]


def apply_filters(query: Query, filters: Iterable[Filter[Any]]) -> Query:
    for comparator, arg in filters:
        query = apply_filter(query, comparator, arg)

    return query


def apply_filter(query: Query, comparator: ComparisonFunc[common.T], arg: common.Filterable[common.T]) -> Query:
    if arg is None:
        return query
    elif isinstance(arg, Iterable) and not isinstance(arg, str):
        return query.filter(comparator.__self__.in_(arg))
    else:
        return query.filter(comparator(arg))
