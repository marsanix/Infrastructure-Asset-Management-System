"""Import semua model agar Flask-Migrate bisa detect."""
from .account import Account, RefreshToken
from .role import Role, Permission, RolePermission
from .department import Department
from .location import Location
from .category import Category
from .brand import Brand
from .employee import Employee
from .model_device import DeviceModel
from .asset import Asset
from .network_detail import NetworkDetail
from .asset_credential import AssetCredential
from .audit_log import AuditLog
from .itsm import Change, Incident, Problem, Request, IncidentProblem
