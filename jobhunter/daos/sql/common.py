from typing import Any, Callable, Iterable, Optional, Tuple, TypeVar, Union

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

import jobhunter.config

SQLALCHEMY_ENGINE = sqlalchemy.create_engine(jobhunter.config.SQL_URL)
METADATA = sqlalchemy.MetaData(SQLALCHEMY_ENGINE)

Base = declarative_base()
Session = sessionmaker(bind=SQLALCHEMY_ENGINE)

T = TypeVar('T')
Filterable = Optional[Union[T, Iterable[T]]]
ComparisonFunc = Callable[[T], BinaryExpression]
Filter = Tuple[Filterable[T], ComparisonFunc[T]]


def apply_filters(query: Query, filters: Iterable[Filter[Any]]) -> Query:
    for comparator, arg in filters:
        query = apply_filter(query, comparator, arg)

    return query


def apply_filter(query: Query, comparator: ComparisonFunc[T], arg: Filterable[T]) -> Query:
    if arg is None:
        return query
    elif isinstance(arg, Iterable) and not isinstance(arg, str):
        return query.filter(comparator.__self__.in_(arg))
    else:
        return query.filter(comparator(arg))
