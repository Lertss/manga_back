from common.models import Comment, MangaRating


def comment_object_filter(model: str, slug) -> Comment:
    """Returns comments filtered by word and model type (manga or chapter)"""
    if model == "manga":
        return Comment.objects.filter(manga__slug=slug)
    elif model == "chapter":
        return Comment.objects.filter(chapter__slug=slug)
    else:
        return Comment.objects.none()


def mangarating_object_filter(
    manga_id,
    user_id,
) -> MangaRating:
    """Returns the manga rating specified by the user"""
    return MangaRating.objects.filter(manga=manga_id, user=user_id).first()
