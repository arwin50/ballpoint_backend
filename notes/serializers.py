from rest_framework import serializers
from .models import NoteDocument, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'label', 'color']

    def to_internal_value(self, data):
        label = data.get('label')
        color = data.get('color', '')
        
        if not label:
            raise serializers.ValidationError({'label': 'This field is required.'})
        
        # Validate and return the data as a dictionary
        return {'label': label, 'color': color}

class NoteDocumentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = NoteDocument
        fields = ['noteID', 'title', 'categories', 'notesContent', 'date']

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        note_document = NoteDocument.objects.create(**validated_data)
        
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(**category_data)
            note_document.categories.add(category)
        
        return note_document

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', [])
        instance.title = validated_data.get('title', instance.title)
        instance.notesContent = validated_data.get('notesContent', instance.notesContent)
        instance.date = validated_data.get('date', instance.date)
        instance.save()

        if categories_data:
            category_instances = []
            for category_data in categories_data:
                category, created = Category.objects.get_or_create(**category_data)
                category_instances.append(category)
            instance.categories.set(category_instances)

        return instance
