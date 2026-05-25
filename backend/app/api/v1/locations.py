"""Location CRUD."""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load
from . import api_v1
from .base_crud import register_crud
from ...models.location import Location


class LocationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name        = fields.Str(required=True,
                              validate=[validate.Length(min=1, max=100),
                                        validate.Regexp(r'^[\w\s\-\.,/]+$',
                                                        error='Invalid characters in name')])
    description = fields.Str(load_default=None, validate=validate.Length(max=500), allow_none=True)
    is_active   = fields.Bool(load_default=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(l: Location) -> dict:
    return {
        'id':          l.id,
        'name':        l.name,
        'description': l.description,
        'is_active':   l.is_active,
        'created_at':  l.created_at.isoformat(),
        'updated_at':  l.updated_at.isoformat(),
    }


_schema = LocationSchema()

register_crud(
    blueprint         = api_v1,
    url_prefix        = '/locations',
    model_class       = Location,
    create_schema     = _schema,
    update_schema     = _schema,
    serializer        = _serialize,
    permission_module = 'location',
    searchable_fields = [Location.name],
)
