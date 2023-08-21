# common/serializers.py
from rest_framework import serializers


from users.models import MangaList
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CommentSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'timestamp']

    def update(self, instance, validated_data):
        # Оновлення полів коментаря, якщо потрібно
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance






