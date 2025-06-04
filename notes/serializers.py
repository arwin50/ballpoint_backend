from rest_framework import serializers
from .models import NoteDocument, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'label', 'color', 'user']
        read_only_fields = ['user']  # Make user field read-only

    def create(self, validated_data):
        # Get the current user from the context
        user = self.context['request'].user
        # Create the category with the current user
        category = Category.objects.create(user=user, **validated_data)
        return category

    def to_internal_value(self, data):
        label = data.get('label')
        color = data.get('color', '')
        
        if not label:
            raise serializers.ValidationError({'label': 'This field is required.'})
        
        return {'label': label, 'color': color}

class CategoryIDSerializer(serializers.Serializer):
    categories = serializers.ListField(
        child=serializers.CharField(),  # Specify that the list contains strings
        required=True,
        help_text="List of category IDs"
    )

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
        for category_data in categories_data:
            # Create category with the current user
            category = Category.objects.create(
                user=user,
                label=category_data['label'],
                color=category_data.get('color', '')
            )
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
                # Create or get category with the current user
                category, created = Category.objects.get_or_create(
                    user=instance.user,
                    label=category_data['label'],
                    defaults={'color': category_data.get('color', '')}
                )
                category_instances.append(category)
            instance.categories.set(category_instances)

        return instance
