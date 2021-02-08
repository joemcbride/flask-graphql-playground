import datetime
from arid import make_schema, Text, DateTime, Relationship, Fields


class Role:
    fields = Fields(
        name=Text(is_required=True),
        assigned_to=Relationship(ref="User.role", many=True),
    )


class User:
    fields = {
        "name": Text(is_required=True),
        "email": Text(is_unique=True),
        "role": Relationship(ref="Role.assigned_to", many=True),
        "scorecards": Relationship(ref="Scorecard.created_by", many=True),
    }


class ScorecardType:
    name = "Scorecard"
    access = {"create": lambda: True, "read": lambda: True}
    fields = {
        "name": Text(is_required=True),
        "full_name": Text(),
        "folder": Text(),
        "created_by": Relationship(ref="User.scorecards", is_required=True),
        "created": DateTime(),
    }

    def resolve_scorecard(root, _info, id):
        return ScorecardDto(
            name=f"single from func {id}",
            created=datetime.datetime.utcnow(),
            created_by=1,
        )

    def resolve_allScorecards(root, _info):
        return [
            ScorecardDto(
                name="from func",
                created=datetime.datetime.utcnow(),
                created_by=1,
            )
        ]

    def resolve_created_by(
        scorecard,
        _info,
    ):
        return UserDto(name=f"from func {scorecard.created_by}")


class ScorecardDto:
    def __init__(self, name, created, created_by):
        self.name = name
        self.created = created
        self.created_by = created_by


class UserDto:
    def __init__(self, name):
        self.name = name


schema = make_schema([User, ScorecardType, Role])
