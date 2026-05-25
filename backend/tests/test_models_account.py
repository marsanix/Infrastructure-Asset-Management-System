"""
Unit tests: models/account.py
Test password hashing, brute-force lockout, dan soft delete.
"""
import pytest


class TestAccountPasswordHashing:
    """Test bcrypt password helper methods."""

    def test_set_password_stores_hash_not_plaintext(self, make_account):
        account = make_account(username="hash_test", password="MyP@ssword1!")
        assert account.password_hash != "MyP@ssword1!"
        assert account.password_hash.startswith("$2b$")  # bcrypt prefix

    def test_check_password_correct(self, make_account):
        account = make_account(username="check_test", password="Correct@Pass1!")
        assert account.check_password("Correct@Pass1!") is True

    def test_check_password_incorrect(self, make_account):
        account = make_account(username="wrong_pass", password="RealPass@123!")
        assert account.check_password("WrongPassword") is False

    def test_check_password_case_sensitive(self, make_account):
        account = make_account(username="case_test", password="CasePass@123!")
        assert account.check_password("casepass@123!") is False

    def test_set_password_changes_hash(self, make_account, db_session):
        account = make_account(username="change_pw", password="OldPass@123!")
        old_hash = account.password_hash
        account.set_password("NewPass@456!")
        db_session.flush()
        assert account.password_hash != old_hash
        assert account.check_password("NewPass@456!")


class TestAccountBruteForce:
    """Test increment_failed_login dan auto-lock."""

    def test_increment_failed_login_increments_counter(self, make_account, db_session):
        account = make_account(username="bf_test1")
        account.increment_failed_login()
        assert account.failed_login_count == 1
        assert account.is_locked is False

    def test_locks_after_max_attempts(self, make_account, db_session):
        account = make_account(username="bf_test2")
        for _ in range(5):
            account.increment_failed_login(max_attempts=5)
        assert account.is_locked is True
        assert account.failed_login_count == 5

    def test_not_locked_before_max_attempts(self, make_account):
        account = make_account(username="bf_test3")
        for _ in range(4):
            account.increment_failed_login(max_attempts=5)
        assert account.is_locked is False

    def test_reset_failed_login_unlocks(self, make_account, db_session):
        account = make_account(username="bf_test4")
        for _ in range(5):
            account.increment_failed_login()
        assert account.is_locked is True

        account.reset_failed_login()
        assert account.failed_login_count == 0
        assert account.is_locked is False

    def test_custom_max_attempts(self, make_account):
        account = make_account(username="bf_test5")
        for _ in range(3):
            account.increment_failed_login(max_attempts=3)
        assert account.is_locked is True


class TestAccountSoftDelete:
    """Test is_deleted property."""

    def test_new_account_not_deleted(self, make_account):
        account = make_account(username="not_deleted")
        assert account.is_deleted is False
        assert account.deleted_at is None

    def test_deleted_account_returns_true(self, make_account, db_session):
        from datetime import datetime, timezone
        account = make_account(username="to_delete")
        account.deleted_at = datetime.now(timezone.utc)
        db_session.flush()
        assert account.is_deleted is True
