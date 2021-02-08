import datetime
from aniso8601 import parse_date, parse_datetime, parse_time
from graphql import (
    GraphQLError,
    GraphQLScalarType,
)
from graphql.language import StringValueNode, print_ast


class DateTime:
    @staticmethod
    def serialize(value):
        if not isinstance(value, (datetime.datetime, datetime.date)):
            raise GraphQLError(f"DateTime cannot represent value: {repr(value)}")
        return value.isoformat()

    @staticmethod
    def parse_value(value):
        if isinstance(value, datetime.datetime):
            return value
        if not isinstance(value, str):
            raise GraphQLError(
                f"DateTime cannot represent non-string value: {repr(value)}"
            )
        try:
            return parse_datetime(value)
        except ValueError:
            raise GraphQLError(f"DateTime cannot represent value: {repr(value)}")

    @staticmethod
    def parse_literal(node, _variables=None):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(
                f"DateTime cannot represent non-string value: {print_ast(node)}"
            )
        return DateTime.parse_value(node.value)


# TODO: build a "scalar" factory from the types

GraphQLDateTime = GraphQLScalarType(
    name="DateTime",
    serialize=DateTime.serialize,
    parse_value=DateTime.parse_value,
    parse_literal=DateTime.parse_literal,
)

GraphQLTypeReference = GraphQLScalarType(
    name="GraphQLTypeReference",
    serialize=lambda value: str(value),
    parse_value=lambda value: value,
    parse_literal=lambda value_node, _variables: value_node.value,
)
