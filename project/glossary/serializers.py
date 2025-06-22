from rest_framework import serializers
from .models import Term, Category, TermDetail, RelatedTerm

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TermDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermDetail
        fields = ['section_title', 'content', 'image']

class RelatedTermSerializer(serializers.ModelSerializer):
    related_term_title = serializers.CharField(source='related_term.title', read_only=True)

    class Meta:
        model = RelatedTerm
        fields = ['related_term_title', 'relationship_description']

class TermSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    details = TermDetailSerializer(many=True, read_only=True)
    related_terms = RelatedTermSerializer(many=True, read_only=True)

    class Meta:
        model = Term
        fields = ['id', 'title', 'description', 'image', 'category', 'details', 'related_terms']
