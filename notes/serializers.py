from rest_framework import serializers
from .models import NoteDocument, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['label', 'color']

    def to_internal_value(self, data):
        label = data.get('label')
        color = data.get('color', '')
        
        if not label:
            raise serializers.ValidationError({'label': 'This field is required.'})
        
        category, created = Category.objects.get_or_create(label=label, defaults={'color': color})
        return category

class NoteDocumentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = NoteDocument
        fields = ['noteID', 'title', 'categories', 'notesContent', 'date']

    def create(self, validated_data):
        user = self.context['request'].user  # Get the current user
        categories_data = validated_data.pop('categories', [])
        
        validated_data.pop('user', None)
        
        # Create the NoteDocument without passing 'user' in validated_data
        note_document = NoteDocument.objects.create(**validated_data, user=user)

        # Add the categories to the note document
        for category in categories_data:
            category_instance = Category.objects.get(id=category['id'])  
            note_document.categories.add(category_instance)

        return note_document

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', [])
        instance.title = validated_data.get('title', instance.title)
        instance.notesContent = validated_data.get('notesContent', instance.notesContent)
        instance.date = validated_data.get('date', instance.date)
        instance.save()

        if categories_data:
            # Updating the categories
            instance.categories.set(categories_data)

        return instance
