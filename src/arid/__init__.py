from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLArgument,
    GraphQLID,
    GraphQLString,
    GraphQLNonNull,
    GraphQLList,
    GraphQLScalarType,
)
from .types import GraphQLDateTime, GraphQLTypeReference

Fields = lambda **kwargs: type("Fields", (), kwargs)()

META_EXTENSION = "_meta"


def lower_first(name_str):
    first, *others = name_str.split()
    return "".join([first.lower(), *map(str.title, others)])


def camel(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


class Text:
    def __init__(self, is_required=False, is_unique=False):
        self.is_required = is_required
        self.is_unique = is_unique
        self.graphql_type = GraphQLString


class DateTime:
    def __init__(self, is_required=False, is_unique=False):
        self.is_required = is_required
        self.is_unique = is_unique
        self.graphql_type = GraphQLDateTime


class Relationship:
    def __init__(self, ref, many=False, is_required=False):
        self.ref = ref
        self.many = many
        self.is_required = is_required


class AccessOptions:
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"


def name_from_resolver_func(name):
    idx = name.find("_")
    return name[idx + 1 :]


def get_resolver_funcs(cls):
    return {
        f"{name_from_resolver_func(attr)}": getattr(cls, attr)
        for attr in cls.__dict__.keys()
        if attr.startswith("resolve")
    }


def get_fields_from_class_attributes(cls, resolvers):
    return get_fields_from_dict(
        {
            attr: getattr(type(cls), attr)
            for attr in type(cls).__dict__.keys()
            if attr[:2] != "__" and not attr.startswith("resolve")
        },
        resolvers,
    )


def get_fields_from_dict(dictionary, resolvers):
    # TODO: format name to camelCase - would need to support re-binding to original field on query
    fields = {
        f"{name}": make_field(name, config, resolvers)
        for name, config in dictionary.items()
    }

    # filter None values
    fields = {k: v for k, v in fields.items() if v is not None}

    return fields


def match_resolver(resolvers, name):
    if resolvers and name in resolvers:
        return resolvers[name]
    return None


def make_field(name, config, resolvers):

    meta = {}

    if isinstance(config, Relationship):
        idx = config.ref.find(".")
        ref_name = config.ref[:idx]
        meta["ref"] = ref_name
        meta["many"] = config.many
        meta["is_required"] = config.is_required
        return_type = GraphQLTypeReference
    else:
        return_type = getattr(config, "graphql_type")

    if getattr(config, "is_required", False):
        return_type = GraphQLNonNull(return_type)

    resolver = match_resolver(resolvers, name)

    return GraphQLField(
        return_type, resolve=resolver, extensions={META_EXTENSION: meta}
    )


def make_schema(lists):
    query_fields = {}
    all_types = {}

    for l in lists:
        resolvers = getattr(l, "resolvers", None)
        if not resolvers:
            resolvers = get_resolver_funcs(l)

        if not isinstance(l.fields, dict):
            fields = get_fields_from_class_attributes(l.fields, resolvers)
        else:
            fields = get_fields_from_dict(l.fields, resolvers)

        type_name = getattr(l, "name", l.__name__)

        objType = GraphQLObjectType(name=type_name, fields=fields)
        all_types[type_name] = objType

        all_field_name = f"all{type_name}s"
        resolver = match_resolver(resolvers, all_field_name)

        all_field = GraphQLField(GraphQLList(objType), resolve=resolver)
        query_fields[all_field_name] = all_field

        single_field_name = lower_first(type_name)
        resolver = match_resolver(resolvers, single_field_name)
        single_field = GraphQLField(
            objType,
            resolve=resolver,
            args={"id": GraphQLArgument(GraphQLNonNull(GraphQLID))},
        )
        query_fields[single_field_name] = single_field

    def apply_references(gql_type):
        for field_name, field in gql_type.fields.items():
            if field.extensions and META_EXTENSION in field.extensions:
                meta = field.extensions[META_EXTENSION]
                if "ref" in meta:
                    ref_type = all_types[meta["ref"]]
                    if meta["is_required"]:
                        ref_type = GraphQLNonNull(ref_type)
                    if meta["many"]:
                        ref_type = GraphQLNonNull(GraphQLList(GraphQLNonNull(ref_type)))
                    field.type = ref_type

            if hasattr(field, "fields"):
                apply_references(field.fields)

    # replase GraphQLTypeReference fields with the referenced GraphQL type
    for type_name, gql_type in all_types.items():
        apply_references(gql_type)

    return GraphQLSchema(query=GraphQLObjectType(name="Query", fields=query_fields))
