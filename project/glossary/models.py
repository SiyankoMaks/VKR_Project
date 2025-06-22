from django.db import models

# Модель категории терминов
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name


# Модель термина
class Term(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="terms")
    title = models.CharField(max_length=255)
    description = models.TextField()  # Описание термина
    image = models.ImageField(upload_to='term_images/', null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


# Модель для связанных терминов
class RelatedTerm(models.Model):
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name='related_from')
    related_terms = models.ManyToManyField('Term', related_name='related_to')
    relationship_description = models.TextField(null=True, blank=True)

    def str(self):
        return f"Связано с {self.term.title}"


# Детали термина
class TermDetail(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="details")
    section_title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='term_details/', null=True, blank=True)

    def __str__(self):
        return f"{self.section_title} for {self.term.title}"

# Рекомендации для IT-специалистов
class ProfessionRecommendation(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='recommendations')
    quote_about_profession = models.TextField()
    video_about_profession = models.TextField(blank=True, null=True)
    quote_about_path = models.TextField()
    video_about_path = models.TextField(blank=True, null=True)
    roadmap_image = models.ImageField(upload_to='roadmaps/', blank=True, null=True)

    def str(self):
        return f"Рекомендации для {self.term.title}"
