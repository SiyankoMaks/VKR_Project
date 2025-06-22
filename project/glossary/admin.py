from django.contrib import admin
from django import forms
from .models import Category, Term, TermDetail, RelatedTerm, ProfessionRecommendation
from django.utils.safestring import mark_safe

class RelatedTermAdminForm(forms.ModelForm):
    class Meta:
        model = RelatedTerm
        fields = ['term', 'related_terms', 'relationship_description']

    def clean(self):
        cleaned_data = super().clean()
        term = cleaned_data.get('term')
        related_terms = cleaned_data.get('related_terms')

        if related_terms and term in related_terms:
            raise forms.ValidationError("Термин не может быть связан сам с собой.")
        return cleaned_data

class RelatedTermInline(admin.TabularInline):
    model = RelatedTerm
    fk_name = 'term'
    form = RelatedTermAdminForm
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "parent")
    search_fields = ("name",)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category")
    search_fields = ("title",)
    list_filter = ("category",)
    inlines = [RelatedTermInline]

@admin.register(TermDetail)
class TermDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "section_title", "term")
    search_fields = ("section_title", "term__title")
    list_filter = ("term",)

@admin.register(RelatedTerm)
class RelatedTermAdmin(admin.ModelAdmin):
    form = RelatedTermAdminForm
    list_display = ("id", "term", "relationship_description")
    filter_horizontal = ('related_terms',)
    search_fields = ("term__title", "relationship_description")
    list_filter = ("term",)


@admin.register(ProfessionRecommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "term", "short_quote", "has_video")
    search_fields = ("term__title", "quote_about_profession", "quote_about_path")
    fields = (
        "term",
        "quote_about_profession",
        "video_about_profession",
        "video_about_profession_preview",
        "quote_about_path",
        "video_about_path",
        "video_about_path_preview",
        "roadmap_image",
        "roadmap_image_preview",
    )
    readonly_fields = (
        "video_about_profession_preview",
        "video_about_path_preview",
        "roadmap_image_preview",
    )

    def short_quote(self, obj):
        return obj.quote_about_profession[:50]

    def has_video(self, obj):
        return bool(obj.video_about_profession or obj.video_about_path)
    has_video.boolean = True
    has_video.short_description = "Есть видео"

    def video_about_profession_preview(self, obj):
        return mark_safe(obj.video_about_profession) if obj.video_about_profession else "—"
    video_about_profession_preview.short_description = "Предпросмотр: О профессии"

    def video_about_path_preview(self, obj):
        return mark_safe(obj.video_about_path) if obj.video_about_path else "—"
    video_about_path_preview.short_description = "Предпросмотр: Пример работ"

    def roadmap_image_preview(self, obj):
        if obj.roadmap_image:
            return mark_safe(f'<img src="{obj.roadmap_image.url}" style="max-width: 300px; border-radius: 8px;">')
        return "—"
    roadmap_image_preview.short_description = "Предпросмотр: Дорожная карта"