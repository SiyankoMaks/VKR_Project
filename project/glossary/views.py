from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models.functions import Substr
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
import re
from collections import defaultdict

from .models import Category, ProfessionRecommendation, Term, TermDetail, RelatedTerm
from .serializers import TermSerializer, CategorySerializer


def index(request):
    categories = Category.objects.order_by('name')
    return render(request, 'glossary/index.html', {'categories': categories})

def category_terms(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    terms = Term.objects.filter(category=category)
    return render(request, 'glossary/category_terms.html', {'category': category, 'terms': terms})

def all_terms(request):
    sort_order = request.GET.get('sort', 'asc')
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    selected_letter = request.GET.get('letter', '').strip()
    page_number = request.GET.get('page', 1)

    terms = Term.objects.all()
    categories = Category.objects.all()

    if category_id:
        terms = terms.filter(category_id=category_id)

    if search_query:
        terms = terms.filter(title__icontains=search_query)

    if selected_letter:
        terms = terms.annotate(first_letter=Substr('title', 1, 1))
        terms = terms.filter(first_letter__iexact=selected_letter.upper())

    terms = terms.order_by('-title' if sort_order == 'desc' else 'title')

    paginator = Paginator(terms, 10)
    page_obj = paginator.get_page(page_number)

    all_letters_set = set()
    for term in Term.objects.all():
        match = re.match(r'^\(?([А-ЯA-Zа-яa-z0-9])', term.title)
        if match:
            all_letters_set.add(match.group(1).upper())

    all_letters = sorted(all_letters_set, key=lambda x: (not x.isalpha(), x))

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'sort_order': sort_order,
        'search_query': search_query,
        'selected_letter': selected_letter,
        'available_letters': all_letters,
    }
    return render(request, 'glossary/all_terms.html', context)

def term_detail(request, term_id):
    term = get_object_or_404(Term, id=term_id)
    term_details = TermDetail.objects.filter(term=term)

    # Группировка связанных терминов по описанию
    related_term_entries = RelatedTerm.objects.filter(term=term).prefetch_related('related_terms')
    related_terms_grouped = defaultdict(list)

    for entry in related_term_entries:
        description = entry.relationship_description or ""
        for related in entry.related_terms.all():
            related_terms_grouped[description].append(related)

    return_from = request.GET.get('from')
    category_id = request.GET.get('category_id')
    rec_id = request.GET.get('rec_id')

    context = {
        'term': term,
        'term_details': term_details,
        'related_terms_grouped': dict(related_terms_grouped),  # ключ: описание, значение: список Term
        'return_from': return_from,
        'category_id': category_id,
        'rec_id': rec_id,
    }
    return render(request, 'glossary/term_detail.html', context)

def add_related_terms(request, term_id):
    if request.method == 'POST':
        term = get_object_or_404(Term, id=term_id)
        raw_input = request.POST.get('related_titles', '')
        description = request.POST.get('relationship_description', '')
        titles = [title.strip() for title in raw_input.split(',') if title.strip()]

        for title in titles:
            try:
                related = Term.objects.get(title__iexact=title)
                if related != term and not RelatedTerm.objects.filter(term=term, related_term=related).exists():
                    RelatedTerm.objects.create(term=term, related_term=related, relationship_description=description)
            except Term.DoesNotExist:
                messages.warning(request, f'Термин "{title}" не найден.')

        messages.success(request, 'Связанные термины успешно добавлены.')
        return redirect('term_detail', term_id=term.id)

def recommendations_view(request):
    terms_with_recs = ProfessionRecommendation.objects.select_related('term').all()
    return render(request, 'glossary/recommendations_list.html', {'recommendations_list': terms_with_recs})

def recommendation_detail(request, rec_id):
    recommendation = get_object_or_404(ProfessionRecommendation, id=rec_id)
    return render(request, 'glossary/recommendation_detail.html', {
        'term': recommendation.term,
        'recommendation': recommendation
    })


# API (для администратора)
class TermListAPIView(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAdminUser]

class TermDetailAPIView(generics.RetrieveAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAdminUser]

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]