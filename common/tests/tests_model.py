from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from common.models import Comment, MangaRating
from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag
from users.models import CustomUser


class CommentModelTest(TestCase):
    """
    Test suite for the Comment model.
    """

    def setUp(self):
        """
        Set up test data for Comment model tests.

        Returns:
            None
        """
        self.user = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)
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
        self.chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            created_at=timezone.now(),
            slug=None,
        )

    def test_create_comment(self):
        """
        Test creating a comment and its fields.

        Returns:
            None
        """
        comment = Comment.objects.create(
            user=self.user,
            manga=self.manga,
            chapter=self.chapter,
            content="Test Comment",
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.manga, self.manga)
        self.assertEqual(comment.chapter, self.chapter)
        self.assertEqual(comment.content, "Test Comment")
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

    def test_comment_str_method(self):
        """
        Test the __str__ method of Comment model.

        Returns:
            None
        """
        comment = Comment.objects.create(user=self.user, manga=self.manga, content="Test Comment")
        self.assertEqual(str(comment), f"Comment by {self.user.username}")

    def test_comment_auto_now_add(self):
        """
        Test auto_now_add for created_at field in Comment model.

        Returns:
            None
        """
        comment = Comment.objects.create(user=self.user, manga=self.manga, content="Test Comment")
        self.assertAlmostEqual(comment.created_at, timezone.now(), delta=timedelta(seconds=5))

    def test_comment_auto_now(self):
        """
        Test auto_now for updated_at field in Comment model.

        Returns:
            None
        """
        comment = Comment.objects.create(user=self.user, manga=self.manga, content="Test Comment")
        comment.content = "Updated Content"
        comment.save()
        self.assertGreater(comment.updated_at, comment.created_at)


class MangaRatingModelTest(TestCase):
    """
    Test suite for the MangaRating model.
    """

    def setUp(self):
        """
        Set up test data for MangaRating model tests.

        Returns:
            None
        """
        self.user = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)
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

    def test_manga_rating_auto_now_add(self):
        """
        Test auto_now_add for created_at field in MangaRating model.

        Returns:
            None
        """
        manga_rating = MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        self.assertAlmostEqual(manga_rating.created_at, timezone.now(), delta=timedelta(seconds=5))

    def test_manga_rating_auto_now(self):
        """
        Test auto_now for updated_at field in MangaRating model.

        Returns:
            None
        """
        manga_rating = MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        manga_rating.rating = 5
        manga_rating.save()
        self.assertGreater(manga_rating.updated_at, manga_rating.created_at)

    def test_unique_together_constraint(self):
        """
        Test unique_together constraint for MangaRating model.

        Returns:
            None
        """
        MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        with self.assertRaises(Exception) as context:
            MangaRating.objects.create(user=self.user, manga=self.manga, rating=5)
        self.assertTrue("UNIQUE constraint failed" in str(context.exception))
