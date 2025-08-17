from io import BytesIO

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image

from manga.models import Author, Category, Chapter, Country, Genre, Manga, Tag


class MangaModelTest(TestCase):
    """
    Test suite for the Manga model.
    """

    def setUp(self):
        """
        Set up test data for Manga model tests.

        Returns:
            None
        """
        self.category = Category.objects.create(category_name="Manga")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.country = Country.objects.create(country_name="Japan")
        self.genre = Genre.objects.create(genre_name="Action")
        self.tag = Tag.objects.create(tag_name="Alchemy")

    def create_manga(
        self,
        name_manga="Test Manga",
        name_original="Original Name",
        english_only_field="Test_English",
        decency=True,
        review="Test Review",
        slug=None,
    ):
        """
        Helper method to create a Manga instance for testing.

        Args:
            name_manga (str): Name of the manga.
            name_original (str): Original name.
            english_only_field (str): English field.
            decency (bool): Decency flag.
            review (str): Review text.
            slug (str, optional): Slug for manga.

        Returns:
            Manga: The created Manga instance.
        """
        img = Image.new("RGB", (100, 100), color="red")
        img_io = BytesIO()
        img.save(img_io, "PNG")
        avatar = SimpleUploadedFile("test_avatar.png", img_io.getvalue(), content_type="image/png")
        thumbnail = SimpleUploadedFile("test_thumbnail.png", b"", content_type="image/png")
        manga = Manga.objects.create(
            category=self.category,
            name_manga=name_manga,
            name_original=name_original,
            english_only_field=english_only_field,
            decency=decency,
            review=review,
            avatar=avatar,
            thumbnail=thumbnail,
            slug=slugify(english_only_field) if not slug else slug,
        )
        manga.author.add(self.author)
        manga.country.add(self.country)
        manga.genre.add(self.genre)
        manga.tags.add(self.tag)
        return manga

    def test_str_representation(self):
        """
        Test the __str__ method of Manga model.

        Returns:
            None
        """
        manga = self.create_manga()
        self.assertEqual(str(manga), "Test Manga")

    def test_get_avatar(self):
        """
        Test get_avatar_url method of Manga model.

        Returns:
            None
        """
        manga = self.create_manga()
        self.assertEqual(manga.get_avatar_url(), manga.avatar.url)

    def test_get_absolute_url(self):
        """
        Test get_absolute_url method of Manga model.

        Returns:
            None
        """
        manga = self.create_manga()
        self.assertEqual(manga.get_absolute_url(), f"/{manga.slug}/")

    def test_get_thumbnail_url(self):
        """
        Test get_thumbnail_url method of Manga model.

        Returns:
            None
        """
        manga = self.create_manga()
        self.assertEqual(manga.get_thumbnail_url(), manga.thumbnail.url)

    def make_thumbnail(self, avatar):
        """
        Helper method to create a thumbnail from an avatar image.

        Args:
            avatar (File): The avatar image file.

        Returns:
            File: The thumbnail image file.
        """
        try:
            img = Image.open(avatar)
        except Exception as e:
            print(f"Error opening image: {e}")
            raise
        img = img.resize((120, 170))
        thumb_io = BytesIO()
        img.save(thumb_io, "PNG", quality=85)
        thumbnail = File(thumb_io, name=avatar.name)
        return thumbnail

    def test_save_method(self):
        """
        Test save method and slug generation for Manga model.

        Returns:
            None
        """
        manga = self.create_manga()
        self.assertEqual(manga.slug, "test_english")
        # Test saving without specifying a slug
        manga2 = self.create_manga(english_only_field="Test_English_2", slug=None)
        self.assertEqual(manga2.slug, "test_english_2")


class AuthorModelTest(TestCase):
    """
    Test suite for the Author model.
    """

    def test_str_representation(self):
        """
        Test the __str__ method of Author model.

        Returns:
            None
        """
        author = Author(first_name="John", last_name="Doe")
        self.assertEqual(str(author), "John, Doe")

    def test_unique_id(self):
        """
        Test unique id generation for Author model.

        Returns:
            None
        """
        author1 = Author.objects.create(first_name="John", last_name="Doe")
        author2 = Author.objects.create(first_name="Jane", last_name="Doe")
        self.assertNotEqual(author1.id, author2.id)


class CountryModelTest(TestCase):
    """
    Test suite for the Country model.
    """

    def test_str_representation(self):
        """
        Test the __str__ method of Country model.

        Returns:
            None
        """
        country = Country(country_name="Ukraine")
        self.assertEqual(str(country), "Ukraine")

    def test_unique_id(self):
        """
        Test unique id generation for Country model.

        Returns:
            None
        """
        country1 = Country.objects.create(country_name="Ukraine")
        country2 = Country.objects.create(country_name="United States")
        self.assertNotEqual(country1.id, country2.id)


class GenreModelTest(TestCase):
    """
    Test suite for the Genre model.
    """

    def test_str_representation(self):
        """
        Test the __str__ method of Genre model.

        Returns:
            None
        """
        genre = Genre(genre_name="Action")
        self.assertEqual(str(genre), "Action")

    def test_unique_id(self):
        """
        Test unique id generation for Genre model.

        Returns:
            None
        """
        genre1 = Genre.objects.create(genre_name="Action")
        genre2 = Genre.objects.create(genre_name="Adventure")
        self.assertNotEqual(genre1.id, genre2.id)


class TagModelTest(TestCase):
    """
    Test suite for the Tag model.
    """

    def test_str_representation(self):
        """
        Test the __str__ method of Tag model.

        Returns:
            None
        """
        tag = Tag(tag_name="Alchemy")
        self.assertEqual(str(tag), "Alchemy")

    def test_unique_id(self):
        """
        Test unique id generation for Tag model.

        Returns:
            None
        """
        tag1 = Tag.objects.create(tag_name="Alchemy")
        tag2 = Tag.objects.create(tag_name="Angels")
        self.assertNotEqual(tag1.id, tag2.id)


class CategoryModelTest(TestCase):
    """
    Test suite for the Category model.
    """

    def test_str_representation(self):
        """
        Test the __str__ method of Category model.

        Returns:
            None
        """
        category = Category(category_name="Manga")
        self.assertEqual(str(category), "Manga")

    def test_unique_id(self):
        """
        Test unique id generation for Category model.

        Returns:
            None
        """
        category1 = Category.objects.create(category_name="Manga")
        category2 = Category.objects.create(category_name="Comics")
        self.assertNotEqual(category1.id, category2.id)


class ChapterModelTest(TestCase):
    """
    Test suite for the Chapter model.
    """

    def setUp(self):
        """
        Set up test data for Chapter model tests.

        Returns:
            None
        """
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

    def test_create_chapter(self):
        """
        Test creating a Chapter instance and its fields.

        Returns:
            None
        """
        chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            created_at=timezone.now(),
            slug=None,
        )
        self.assertEqual(chapter.manga, self.manga)
        self.assertEqual(chapter.title, "Chapter Title")
        self.assertEqual(chapter.chapter_number, 1)
        self.assertEqual(chapter.volume, 1)
        self.assertIsNotNone(chapter.slug)

    def test_data_g_method(self):
        """
        Test data_g method of Chapter model.

        Returns:
            None
        """
        chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            created_at=timezone.now(),
            slug=None,
        )
        expected_date = timezone.now().strftime("%m/%d/%Y")
        self.assertEqual(chapter.data_g(), expected_date)

    def test_slug_generation(self):
        """
        Test slug generation for Chapter model.

        Returns:
            None
        """
        chapter = Chapter.objects.create(
            manga=self.manga,
            title="Chapter Title",
            chapter_number=1,
            volume=1,
            created_at=timezone.now(),
            slug=None,
        )
        expected_slug = f"{self.manga.english_only_field.lower()}-1-1"
        self.assertEqual(chapter.slug, expected_slug)
