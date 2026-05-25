"""Category CRUD."""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load
from . import api_v1
from .base_crud import register_crud
from ...models.category import Category


class CategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name        = fields.Str(required=True,
                              validate=[validate.Length(min=1, max=50),
                                        validate.Regexp(r'^[\w\s\-]+$',
                                                        error='Invalid characters')])
    description = fields.Str(load_default=None, validate=validate.Length(max=500), allow_none=True)
    is_active   = fields.Bool(load_default=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(c: Category) -> dict:
    return {
        'id':          c.id,
        'name':        c.name,
        'description': c.description,
        'is_active':   c.is_active,
        'created_at':  c.created_at.isoformat(),
        'updated_at':  c.updated_at.isoformat(),
    }


_schema = CategorySchema()

register_crud(
    blueprint         = api_v1,
    url_prefix        = '/categories',
    model_class       = Category,
    create_schema     = _schema,
    update_schema     = _schema,
    serializer        = _serialize,
    permission_module = 'category',
    searchable_fields = [Category.name],
)
