"""
Unit tests: models/role.py
Test RBAC — has_permission dan Role-Permission relationship.
"""


class TestRoleHasPermission:
    def test_role_with_permission_returns_true(self, make_role):
        role = make_role(name="TestRole", permissions=["asset:read", "asset:create"])
        assert role.has_permission("asset:read") is True

    def test_role_without_permission_returns_false(self, make_role):
        role = make_role(name="LimitedRole", permissions=["asset:read"])
        assert role.has_permission("asset:delete") is False

    def test_empty_permissions_returns_false(self, make_role):
        role = make_role(name="EmptyRole", permissions=[])
        assert role.has_permission("asset:read") is False

    def test_permission_name_case_sensitive(self, make_role):
        role = make_role(name="CaseRole", permissions=["asset:read"])
        assert role.has_permission("Asset:Read") is False
        assert role.has_permission("asset:read") is True

    def test_multiple_permissions_all_accessible(self, make_role):
        perms = ["asset:read", "asset:create", "asset:update", "asset:delete", "account:read"]
        role = make_role(name="FullRole", permissions=perms)
        for perm in perms:
            assert role.has_permission(perm) is True
