"""Employee CRUD — dengan relasi department di response."""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load
from . import api_v1
from .base_crud import register_crud
from ...models.employee import Employee


class EmployeeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name          = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    email         = fields.Email(load_default=None, allow_none=True)
    phone         = fields.Str(load_default=None,
                                validate=validate.Regexp(r'^[\d\+\-\s\(\)]{0,20}$',
                                                         error='Invalid phone format'),
                                allow_none=True)
    department_id = fields.Int(load_default=None, validate=validate.Range(min=1), allow_none=True)
    is_active     = fields.Bool(load_default=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(e: Employee) -> dict:
    return {
        'id':            e.id,
        'name':          e.name,
        'email':         e.email,
        'phone':         e.phone,
        'department_id': e.department_id,
        'department': {
            'id':   e.department.id,
            'name': e.department.name,
        } if e.department else None,
        'is_active':  e.is_active,
        'created_at': e.created_at.isoformat(),
        'updated_at': e.updated_at.isoformat(),
    }


_schema = EmployeeSchema()

register_crud(
    blueprint         = api_v1,
    url_prefix        = '/employees',
    model_class       = Employee,
    create_schema     = _schema,
    update_schema     = _schema,
    serializer        = _serialize,
    permission_module = 'account',   # pakai permission 'account:read' dst.
    searchable_fields = [Employee.name, Employee.email],
)
