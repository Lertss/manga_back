from django.contrib.auth import get_user_model
from django.test import TestCase
from users.service.service_change_email import existing_user_func, user_instance_func


CustomUser = get_user_model()


class UserInstanceFuncTest(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

    def test_user_instance_func_returns_user(self):
        result_user = user_instance_func("test@example.com")
        self.assertEqual(result_user, self.user)

    def test_user_instance_func_with_nonexistent_user(self):
        with self.assertRaises(CustomUser.DoesNotExist):
            user_instance_func("nonexistent@example.com")


class ExistingUserFuncTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

    def test_existing_user_func_returns_existing_user(self):
        new_user = CustomUser.objects.create_user(
            email="newuser@example.com", username="newuser", password="newpassword"
        )

        result_user = existing_user_func("newuser@example.com", self.user)
        self.assertEqual(result_user, new_user)

    def test_existing_user_func_with_nonexistent_user(self):
        result_user = existing_user_func("nonexistent@example.com", self.user)
        self.assertIsNone(result_user)

    def test_existing_user_func_excludes_user_instance(self):
        result_user = existing_user_func("test@example.com", self.user)
        self.assertIsNone(result_user)


class ExistingUserFuncTestV2(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

    def test_existing_user_func_returns_existing_user(self):
        result_user = existing_user_func("test@example.com", self.user)
        self.assertIsNone(result_user)

    def test_existing_user_func_with_nonexistent_user(self):
        result_user = existing_user_func("nonexistent@example.com", self.user)
        self.assertIsNone(result_user)

    def test_existing_user_func_excludes_current_user(self):
        another_user = CustomUser.objects.create_user(
            email="another@example.com", username="anotheruser", password="anotherpassword"
        )

        result_user = existing_user_func("another@example.com", self.user)
        self.assertEqual(result_user, another_user)
