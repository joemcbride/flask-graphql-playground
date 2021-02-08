import asyncio
from typing import Dict, Any
from graphql import GraphQLError, graphql, graphql_sync


class GraphQLOptions:
    query: None
    operation_name: None
    variables: None


def format_error(error: GraphQLError) -> Dict[str, Any]:
    """
    Format a GraphQL error.
    Given a GraphQLError, format it according to the rules described by the "Response
    Format, Errors" section of the GraphQL Specification.
    """
    if not isinstance(error, GraphQLError):
        raise TypeError("Expected a GraphQLError.")
    formatted: Dict[str, Any] = dict(  # noqa: E701 (pycqa/flake8#394)
        message=error.message or "An unknown error occurred.",
        locations=(
            [location.formatted for location in error.locations]
            if error.locations is not None
            else None
        ),
        path=error.path,
    )
    if error.extensions:
        formatted.update(extensions=error.extensions)
    return formatted


def get_graphql_options(data):
    options = GraphQLOptions()
    options.query = data["query"] if "query" in data else None
    options.operation_name = data["operationName"] if "operationName" in data else None
    options.variables = data["variables"] if "variables" in data else None
    return options


def make_result(execution_result):
    return_result = {"data": execution_result.data}

    if execution_result.errors:
        return_result["errors"] = [format_error(e) for e in execution_result.errors]

    return return_result


def execute(json, schema):
    options = get_graphql_options(json)

    loop = asyncio.new_event_loop()

    async def run_query():
        return graphql_sync(
            schema,
            options.query,
            operation_name=options.operation_name,
            variable_values=options.variables,
        )

    execution_result = loop.run_until_complete(run_query())

    return make_result(execution_result)
