from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import RequestFactory, TestCase
from django.utils import timezone

from common.models import Comment, MangaRating
from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag
from manga.service.service import (
    create_comment,
    get_manga_objects,
    mangalist_filter,
    mangalist_filter_by_user,
    mangalist_remove,
    one_hundred_last_added_chapters,
    random_manga,
    top_manga_comments_annotate_serializer,
    top_manga_last_year_filter_serializer,
    top_manga_objects_annotate_serializer,
)
from users.models import CustomUser, MangaList


class MangaServiceTestCase(TestCase):
    def setUp(self):

        self.category = Category.objects.create(category_name="Manga")

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="Test Manga",
            name_original="Original Name",
            english_only_field="Test_English",
            decency=True,
            review="Test Review",
            slug="test-manga",
        )

    def test_get_manga_objects_existing_slug(self):

        result = get_manga_objects(manga_slug="test-manga")
        self.assertEqual(result, self.manga)

    def test_get_manga_objects_nonexistent_slug(self):

        with self.assertRaises(Manga.DoesNotExist):
            get_manga_objects(manga_slug="nonexistent-slug")


class MangaServiceTest(TestCase):

    def setUp(self):

        self.genre = Genre.objects.create(genre_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(country_name="Afghanistan")
        self.category = Category.objects.create(category_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

        for i in range(1, 101):
            self.manga = Manga.objects.create(
                category=self.category,
                name_manga=f"Test Manga {i}",
                name_original="Original Name",
                english_only_field=f"Test_English_{i}",
                decency=True,
                review=f"Test Review {i}",
                avatar=SimpleUploadedFile(f"test_avatar_{i}.png", b"", content_type="image/png"),
                thumbnail=SimpleUploadedFile(f"test_thumbnail_{i}.png", b"", content_type="image/png"),
                slug=f"test-manga-{i}",
            )

            self.manga.author.add(self.author)
            self.manga.country.add(self.country)
            self.manga.genre.add(self.genre)
            self.manga.tags.add(self.tag)

            self.chapter = Chapter.objects.create(
                manga=self.manga,
                title=f"Chapter Title {i}",
                chapter_number=i,
                volume=i,
                created_at=timezone.now(),
                slug=None,
            )

    def test_one_hundred_last_added_chapters(self):
        # Call the function
        chapter_data = one_hundred_last_added_chapters()

        # Assert that the returned data is a list
        self.assertIsInstance(chapter_data, list)

        # Assert that the list has at most 100 items or less, depending on the available chapters
        self.assertLessEqual(len(chapter_data), 100)
        # Assert that each item in the list is a dictionary
        for chapter in chapter_data:
            self.assertIsInstance(chapter, dict)

            # Assert that required keys are present in the dictionary
            self.assertIn("manga", chapter)
            self.assertIn("title", chapter)


class MangaRandomTest(TestCase):

    def setUp(self):

        self.genre = Genre.objects.create(genre_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(country_name="Afghanistan")
        self.category = Category.objects.create(category_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="manga-1",
            name_original="Original Name",
            english_only_field="manga-1",
            decency=True,
            review="Test Review 1",
            avatar=SimpleUploadedFile("test_avatar_1.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail_1.png", b"", content_type="image/png"),
            slug="manga-1",
        )

        self.manga.author.add(self.author)
        self.manga.country.add(self.country)
        self.manga.genre.add(self.genre)
        self.manga.tags.add(self.tag)

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="manga-2",
            name_original="Original Name",
            english_only_field="manga-2",
            decency=True,
            review="Test Review 1",
            avatar=SimpleUploadedFile("test_avatar_1.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail_1.png", b"", content_type="image/png"),
            slug="manga-2",
        )

        self.manga.author.add(self.author)
        self.manga.country.add(self.country)
        self.manga.genre.add(self.genre)
        self.manga.tags.add(self.tag)

    def test_random_manga_with_two_mangas(self):

        manga_count = Manga.objects.count()
        self.assertEqual(manga_count, 2)

        result = random_manga()

        self.assertEqual(len(result.data), 2)
        self.assertTrue(any("url" in item and item["url"] == "/manga-1/" for item in result.data))
        self.assertTrue(any("url" in item and item["url"] == "/manga-2/" for item in result.data))

    def test_random_manga_with_less_than_two_mangas(self):

        Manga.objects.filter(slug="manga-2").delete()

        result = random_manga()

        self.assertEqual(Manga.objects.count(), 1)
        if result.data:
            self.assertTrue(any("url" in item and item["url"] == "/manga-1/" for item in result.data))
            self.assertTrue(all("url" in item for item in result.data))
        else:
            self.fail("Result data is empty. No Manga objects returned.")


class TopMangaFunctionTest(TestCase):

    def setUp(self):

        self.user1 = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)
        self.user2 = CustomUser.objects.create(username="testuser2", gender="Male", adult=True)

        self.genre = Genre.objects.create(genre_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(country_name="Afghanistan")
        self.category = Category.objects.create(category_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

        self.manga1 = Manga.objects.create(
            category=self.category,
            name_manga="Test Manga1",
            name_original="Original Name",
            english_only_field="Test_English1",
            decency=True,
            review="Test Review",
            avatar=SimpleUploadedFile("test_avatar.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail.png", b"", content_type="image/png"),
            slug="test-manga1",
            created_at=timezone.now() - timedelta(days=10),
        )
        self.manga1.author.add(self.author)
        self.manga1.country.add(self.country)
        self.manga1.genre.add(self.genre)
        self.manga1.tags.add(self.tag)

        self.manga2 = Manga.objects.create(
            category=self.category,
            name_manga="Test Manga2",
            name_original="Original Name",
            english_only_field="Test_English2",
            decency=True,
            review="Test Review",
            avatar=SimpleUploadedFile("test_avatar.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail.png", b"", content_type="image/png"),
            slug="test-manga2",
            created_at=timezone.now(),
        )
        self.manga2.author.add(self.author)
        self.manga2.country.add(self.country)
        self.manga2.genre.add(self.genre)
        self.manga2.tags.add(self.tag)

        # Create sample ratings for testing
        MangaRating.objects.create(user=self.user1, manga=self.manga1, rating=4)
        MangaRating.objects.create(user=self.user2, manga=self.manga1, rating=2)
        MangaRating.objects.create(user=self.user1, manga=self.manga2, rating=4)

        Comment.objects.create(user=self.user1, manga=self.manga1, content="Comment 1")
        Comment.objects.create(user=self.user1, manga=self.manga1, content="Comment 2")
        Comment.objects.create(user=self.user1, manga=self.manga2, content="Comment 3")

    """
    Testing the 'top_manga_last_year_filter_serializer' function
    """

    def test_top_manga_last_year_filter_serializer(self):
        result = top_manga_last_year_filter_serializer()

        # Add your assertions based on your serializer and model structure
        for i in range(1, 3):
            self.assertEqual(len(result.data), 2)  # Assuming only two Manga objects in the last year
            self.assertEqual(result.data[0]["name_manga"], "Test Manga2")
            self.assertEqual(result.data[0]["average_rating"], 4)  # Assuming the average rating is calculated correctly
            self.assertEqual(result.data[1]["average_rating"], 3)
        # Add more assertions as needed based on your specific serializer and model fields

    """
    Testing the 'top_manga_objects_annotate_serializer' function
    """

    def test_top_manga_objects_annotate_serializer(self):

        result = top_manga_objects_annotate_serializer()
        # Add your assertions based on your serializer and model structure
        for i in range(1, 3):
            self.assertEqual(len(result.data), 2)  # Assuming only two Manga objects in the last year
            self.assertEqual(result.data[0]["name_manga"], "Test Manga2")
            self.assertEqual(result.data[0]["average_rating"], 4)  # Assuming the average rating is calculated correctly
            self.assertEqual(result.data[1]["average_rating"], 3)
        # Add more assertions as needed based on your specific serializer and model fields

    """
    Testing the 'top_manga_comments_annotate_serializer' function
    """

    def test_top_manga_comments_annotate_serializer(self):

        result = top_manga_comments_annotate_serializer()

        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]["url"], "/test-manga1/")
        self.assertEqual(result.data[1]["url"], "/test-manga2/")
        comments_count = {manga["id"]: Comment.objects.filter(manga_id=manga["id"]).count() for manga in result.data}
        print(result.data[1]["id"])

        self.assertEqual(comments_count[result.data[0]["id"]], 2)
        self.assertEqual(comments_count[result.data[1]["id"]], 1)


class MangaListFunctionTestCase(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.user = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)
        self.factory = RequestFactory()

        self.genre = Genre.objects.create(genre_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(country_name="Afghanistan")
        self.category = Category.objects.create(category_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

        self.manga = Manga.objects.create(
            category=self.category,
            name_manga="manga-1",
            name_original="Original Name",
            english_only_field="manga-1",
            decency=True,
            review="Test Review 1",
            avatar=SimpleUploadedFile("test_avatar_1.png", b"", content_type="image/png"),
            thumbnail=SimpleUploadedFile("test_thumbnail_1.png", b"", content_type="image/png"),
            slug="manga-1",
        )

        self.manga.author.add(self.author)
        self.manga.country.add(self.country)
        self.manga.genre.add(self.genre)
        self.manga.tags.add(self.tag)

        self.manga_list = MangaList.objects.create(user=self.user, manga=self.manga, name="Reading")

    """
    Testing the 'mangalist_filter_by_user' function
    """

    def test_mangalist_filter_by_user(self):
        # Test if the function returns the correct MangaList objects for a specific user
        filtered_lists = mangalist_filter_by_user(self.user)
        self.assertEqual(filtered_lists.count(), 1)
        self.assertEqual(filtered_lists.first(), self.manga_list)

    def test_mangalist_filter_by_user_no_lists(self):
        # Test if the function returns an empty queryset if the user has no MangaList objects
        user_without_lists = CustomUser.objects.create_user(username="no_lists_user", password="test_password")
        filtered_lists = mangalist_filter_by_user(user_without_lists)
        self.assertEqual(filtered_lists.count(), 0)

    def test_mangalist_filter_by_user_multiple_lists(self):
        # Test if the function returns the correct MangaList objects when the user has multiple lists
        another_manga = Manga.objects.create(
            category=self.category,
            name_manga="Another Test Manga",
            english_only_field="another_test_english_field",
            review="Another Test Review",
            slug="another-test-manga",
        )
        another_manga_list = MangaList.objects.create(user=self.user, manga=another_manga, name="To Read")

        filtered_lists = mangalist_filter_by_user(self.user)
        self.assertEqual(filtered_lists.count(), 2)
        self.assertIn(self.manga_list, filtered_lists)
        self.assertIn(another_manga_list, filtered_lists)

    """
    Testing the 'mangalist_filter' function
    """

    def test_mangalist_filter(self):
        # Test if the function returns the correct MangaList object for the given user and manga_slug
        filtered_list = mangalist_filter(
            request=type("Request", (object,), {"user": self.user}),
            manga_slug="manga-1",
        )
        self.assertEqual(filtered_list, self.manga_list)

    def test_mangalist_filter_no_match(self):
        # Test if the function returns None when there is no match for the given manga_slug and user
        filtered_list = mangalist_filter(
            request=type("Request", (object,), {"user": self.user}),
            manga_slug="nonexistent-manga",
        )
        self.assertIsNone(filtered_list)

    def test_mangalist_filter_different_user(self):
        # Test if the function returns None when the manga is associated with a different user
        another_user = CustomUser.objects.create_user(username="another_user", password="test_password")
        filtered_list = mangalist_filter(
            request=type("Request", (object,), {"user": another_user}),
            manga_slug="manga-1",
        )
        self.assertIsNone(filtered_list)

    """
    Testing the 'mangalist_remove' function
    """

    def test_mangalist_remove(self):
        # Test if the function returns the correct MangaList object for removal based on the provided manga slug
        request_data = {"slug": "manga-1"}
        filtered_list = mangalist_remove(request=type("Request", (object,), {"user": self.user, "data": request_data}))
        self.assertEqual(filtered_list, self.manga_list)

    def test_mangalist_remove_no_match(self):
        # Test if the function returns None when there is no match for the given manga_slug and user
        request_data = {"slug": "nonexistent-manga"}
        filtered_list = mangalist_remove(request=type("Request", (object,), {"user": self.user, "data": request_data}))
        self.assertIsNone(filtered_list)

    def test_mangalist_remove_different_user(self):
        # Test if the function returns None when the manga is associated with a different user
        another_user = CustomUser.objects.create_user(username="another_user", password="test_password")
        request_data = {"slug": "manga-1"}
        filtered_list = mangalist_remove(
            request=type("Request", (object,), {"user": another_user, "data": request_data})
        )
        self.assertIsNone(filtered_list)

    """
    Testing the 'create_comment' function
    """

    def test_create_comment(self):

        content = "This is a test comment."
        create_comment(self.user, manga=get_object_or_404(Manga, slug="manga-1"), content=content)

        comment = Comment.objects.get(user=self.user, manga=self.manga, content=content)
        self.assertIsNotNone(comment)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.manga, self.manga)
        self.assertEqual(comment.content, content)
