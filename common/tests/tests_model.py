from datetime import timedelta

from common.models import Comment, MangaRating
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag
from users.models import CustomUser


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)

        self.genre = Genre.objects.create(genr_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(counts="Afghanistan")
        self.category = Category.objects.create(cat_name="Manga")
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
        self.manga.counts.add(self.country)
        self.manga.genre.add(self.genre)
        self.manga.tags.add(self.tag)

        self.chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            time_prod=timezone.now(),
            slug=None,
        )

    def test_create_comment(self):
        comment = Comment.objects.create(user=self.user, manga=self.manga, chapter=self.chapter, content="Test Comment")

        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.manga, self.manga)
        self.assertEqual(comment.chapter, self.chapter)
        self.assertEqual(comment.content, "Test Comment")
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

    def test_comment_str_method(self):
        comment = Comment.objects.create(user=self.user, manga=self.manga, content="Test Comment")
        self.assertEqual(str(comment), f"Comment by {self.user.username}")

    def test_comment_auto_now_add(self):
        comment = Comment.objects.create(user=self.user, manga=self.manga, content="Test Comment")
        self.assertAlmostEqual(comment.created_at, timezone.now(), delta=timedelta(seconds=5))

    def test_comment_auto_now(self):
        comment = Comment.objects.create(user=self.user, manga=self.manga, content="Test Comment")
        comment.content = "Updated Content"
        comment.save()
        self.assertGreater(comment.updated_at, comment.created_at)


class MangaRatingModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser1", gender="Male", adult=True)

        self.genre = Genre.objects.create(genr_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")
        self.country = Country.objects.create(counts="Afghanistan")
        self.category = Category.objects.create(cat_name="Manga")
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

    def test_manga_rating_str_method(self):
        manga_rating = MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        self.assertEqual(
            str(manga_rating), f"Rating {manga_rating.rating} by {self.user.username} for {self.manga.name_manga}"
        )

    def test_manga_rating_auto_now_add(self):
        manga_rating = MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        self.assertAlmostEqual(manga_rating.created_at, timezone.now(), delta=timedelta(seconds=5))

    def test_manga_rating_auto_now(self):
        manga_rating = MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        manga_rating.rating = 5
        manga_rating.save()
        self.assertGreater(manga_rating.updated_at, manga_rating.created_at)

    def test_unique_together_constraint(self):
        MangaRating.objects.create(user=self.user, manga=self.manga, rating=4)
        with self.assertRaises(Exception) as context:
            MangaRating.objects.create(user=self.user, manga=self.manga, rating=5)

        self.assertTrue("UNIQUE constraint failed" in str(context.exception))
