"""Brand CRUD."""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load
from . import api_v1
from .base_crud import register_crud
from ...models.brand import Brand


class BrandSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name      = fields.Str(required=True,
                            validate=[validate.Length(min=1, max=50),
                                      validate.Regexp(r'^[\w\s\-\.]+$',
                                                      error='Invalid characters')])
    is_active = fields.Bool(load_default=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(b: Brand) -> dict:
    return {
        'id':         b.id,
        'name':       b.name,
        'is_active':  b.is_active,
        'created_at': b.created_at.isoformat(),
        'updated_at': b.updated_at.isoformat(),
    }


_schema = BrandSchema()

register_crud(
    blueprint         = api_v1,
    url_prefix        = '/brands',
    model_class       = Brand,
    create_schema     = _schema,
    update_schema     = _schema,
    serializer        = _serialize,
    permission_module = 'brand',
    searchable_fields = [Brand.name],
)
