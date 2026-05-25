"""
Department CRUD — menggunakan generic CRUD factory.
Serializer explicit: hanya expose field yang diperlukan (anti Excessive Data Exposure).
"""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load
from . import api_v1
from .base_crud import register_crud
from ...models.department import Department


class DepartmentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name        = fields.Str(required=True,
                              validate=[validate.Length(min=1, max=100),
                                        validate.Regexp(r'^[\w\s\-\.]+$',
                                                        error='Invalid characters in name')])
    description = fields.Str(load_default=None, validate=validate.Length(max=500), allow_none=True)
    is_active   = fields.Bool(load_default=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(d: Department) -> dict:
    """Explicit serializer — tidak expose deleted_at, internal timestamps, dll."""
    return {
        'id':          d.id,
        'name':        d.name,
        'description': d.description,
        'is_active':   d.is_active,
        'created_at':  d.created_at.isoformat(),
        'updated_at':  d.updated_at.isoformat(),
    }


_schema = DepartmentSchema()

register_crud(
    blueprint         = api_v1,
    url_prefix        = '/departments',
    model_class       = Department,
    create_schema     = _schema,
    update_schema     = _schema,
    serializer        = _serialize,
    permission_module = 'department',
    searchable_fields = [Department.name],
)
