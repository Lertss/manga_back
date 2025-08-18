from time import sleep

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError

from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag
from users.models import CustomUser, MangaList, Notification


class CustomUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        CustomUser.objects.create(username="testuser", gender="Male", adult=True, slug="test-user")

    def test_get_url(self):
        user = CustomUser.objects.get(id=1)
        self.assertEqual(user.get_url(), "/test-user/")

    def test_get_avatar(self):
        user = CustomUser.objects.get(id=1)
        self.assertEqual(
            user.get_avatar_url(),
            "/media/static/images/avatars/user/none_avatar_user.jpg",
        )

    def test_save_method(self):
        # Test the save method with a new user
        user = CustomUser(username="testuser2", gender="Male", adult=True)
        user.save()
        self.assertEqual(user.slug, "testuser2")
        self.assertEqual(user.avatar, "static/images/avatars/user/none_avatar_user.jpg")

        # Test the save method with an existing user
        user2 = CustomUser(username="testuser", gender="Male", adult=True)

        # Use assertRaises to check if the ValidationError is raised
        with self.assertRaises(DRFValidationError) as context:
            user2.save()

        # Check the error message
        self.assertEqual(
            str(context.exception.detail["username"][0:43]),
            "This login already exists. Enter a new one",
        )

        # Ensure that user2 properties remain unchanged
        self.assertEqual(user2.slug, "testuser")
        self.assertEqual(user2.avatar, "static/images/avatars/user/none_avatar_user.jpg")


class MangaListTest(TestCase):
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

    def test_create_manga_list(self):
        manga_list_item = MangaList.objects.create(user=self.user, manga=self.manga, name="Reading")

        self.assertEqual(manga_list_item.user, self.user)
        self.assertEqual(manga_list_item.manga, self.manga)
        self.assertEqual(manga_list_item.name, "Reading")


class NotificationTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser", gender="Male", adult=True)

        self.category = Category.objects.create(category_name="Manga")

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="Test Manga",
        )

        self.chapter = Chapter.objects.create(manga=self.manga, title="Test Chapter", chapter_number=1, volume=1)

    def test_create_notification(self):
        notification = Notification.objects.create(user=self.user, chapter=self.chapter)

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.chapter, self.chapter)
        self.assertFalse(notification.is_read)

    def test_notification_ordering(self):
        notification1 = Notification.objects.create(user=self.user, chapter=self.chapter)
        notification2 = Notification.objects.create(user=self.user, chapter=self.chapter)
        notification3 = Notification.objects.create(user=self.user, chapter=self.chapter)

        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], notification3)
        self.assertEqual(notifications[1], notification2)
        self.assertEqual(notifications[2], notification1)


class NotificationModelTest(TestCase):
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

    def test_create_notification(self):
        notification = Notification.objects.create(user=self.user, chapter=self.chapter, is_read=False)

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.chapter, self.chapter)
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)

    def test_default_values(self):
        notification = Notification.objects.create(user=self.user, chapter=self.chapter)

        self.assertFalse(notification.is_read)

    def test_ordering(self):
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

        self.assertGreater(notification2.created_at, notification1.created_at)
