"""DeviceModel CRUD — dengan relasi brand & category di response."""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load
from . import api_v1
from .base_crud import register_crud
from ...models.model_device import DeviceModel
from ...models.brand import Brand
from ...models.category import Category
from ...extensions import db


class DeviceModelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name           = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    specifications = fields.Str(load_default=None, validate=validate.Length(max=2000), allow_none=True)
    brand_id       = fields.Int(required=True, validate=validate.Range(min=1))
    category_id    = fields.Int(required=True, validate=validate.Range(min=1))
    is_active      = fields.Bool(load_default=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(m: DeviceModel) -> dict:
    """Explicit serializer — include relasi brand & category."""
    brand = Brand.query.get(m.brand_id) if m.brand_id else None
    category = Category.query.get(m.category_id) if m.category_id else None
    return {
        'id':             m.id,
        'name':           m.name,
        'specifications': m.specifications,
        'brand_id':       m.brand_id,
        'category_id':    m.category_id,
        'is_active':      m.is_active,
        'brand': {
            'id':   brand.id,
            'name': brand.name,
        } if brand else None,
        'category': {
            'id':   category.id,
            'name': category.name,
        } if category else None,
        'created_at': m.created_at.isoformat(),
        'updated_at': m.updated_at.isoformat(),
    }


_schema = DeviceModelSchema()

register_crud(
    blueprint         = api_v1,
    url_prefix        = '/models',
    model_class       = DeviceModel,
    create_schema     = _schema,
    update_schema     = _schema,
    serializer        = _serialize,
    permission_module = 'model',
    searchable_fields = [DeviceModel.name],
)
