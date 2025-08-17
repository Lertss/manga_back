from time import sleep

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag
from users.models import CustomUser, Notification
from users.service.service import get_notifications
from users.service.service_change_email import existing_user_func


class ExistingUserFuncTest(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

    def test_existing_user_func_returns_user(self):

        result_user = existing_user_func("test@example.com", self.user)
        print(self.user)
        self.assertEqual(result_user, self.user)

    def test_existing_user_func_with_nonexistent_user(self):

        result_user = existing_user_func("nonexistent@example.com", self.user)
        self.assertIsNone(result_user)


class GetNotificationsTest(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create(username="testuser", gender="Male", adult=True)

        self.genre = Genre.objects.create(genre_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(country_name="Afghanistan")
        self.category = Category.objects.create(category_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="Test Manga",
            name_original="Original Name",
            english_only_field="Test_English",
            decency=True,
            review="Test Review",
            avatar=SimpleUploadedFile("test_avatar.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail.png", b"", content_type="image/png"),
            slug="test-manga",
        )
        self.manga.author.add(self.author)
        self.manga.country.add(self.country)
        self.manga.genre.add(self.genre)
        self.manga.tags.add(self.tag)

        self.chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            created_at=timezone.now(),
            slug="test-chapter",
        )

    def test_get_unread_notifications(self):
        # Create unread notifications
        unread_notification = Notification.objects.create(user=self.user, chapter=self.chapter, is_read=False)
        # Get unread notifications using the utility function
        result = get_notifications(self.user, unread_only=True)

        # Assert that only the unread notification is retrieved
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], unread_notification)

    def test_get_all_notifications(self):
        # Create two notifications with different created_at times
        notification1 = Notification.objects.create(
            user=self.user,
            chapter=self.chapter,
            is_read=False,
            created_at=timezone.now(),
        )
        sleep(2)
        notification2 = Notification.objects.create(
            user=self.user,
            chapter=self.chapter,
            is_read=False,
            created_at=timezone.now(),
        )

        # Get all notifications using the utility function
        result = get_notifications(self.user, unread_only=False)

        # Assert that both notifications are retrieved and in the correct order
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], notification2)
        self.assertEqual(result[1], notification1)
