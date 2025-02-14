from django import forms
from django.utils.encoding import smart_text
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from codex._vendor.haystack import connections
from codex._vendor.haystack.constants import DEFAULT_ALIAS
from codex._vendor.haystack.query import EmptySearchQuerySet, SearchQuerySet
from codex._vendor.haystack.utils import get_model_ct
from codex._vendor.haystack.utils.app_loading import haystack_get_model


def model_choices(using=DEFAULT_ALIAS):
    choices = [
        (get_model_ct(m), capfirst(smart_text(m._meta.verbose_name_plural)))
        for m in connections[using].get_unified_index().get_indexed_models()
    ]
    return sorted(choices, key=lambda x: x[1])


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"type": "search"}),
    )

    def __init__(self, *args, **kwargs):
        self.searchqueryset = kwargs.pop("searchqueryset", None)
        self.load_all = kwargs.pop("load_all", False)

        if self.searchqueryset is None:
            self.searchqueryset = SearchQuerySet()

        super().__init__(*args, **kwargs)

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return EmptySearchQuerySet()

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        sqs = self.searchqueryset.auto_query(self.cleaned_data["q"])

        if self.load_all:
            sqs = sqs.load_all()

        return sqs

    def get_suggestion(self):
        if not self.is_valid():
            return None

        return self.searchqueryset.spelling_suggestion(self.cleaned_data["q"])


class HighlightedSearchForm(SearchForm):
    def search(self):
        return super().search().highlight()


class FacetedSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop("selected_facets", [])
        super().__init__(*args, **kwargs)

    def search(self):
        sqs = super().search()

        # We need to process each facet to ensure that the field name and the
        # value are quoted correctly and separately:
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                sqs = sqs.narrow('%s:"%s"' % (field, sqs.query.clean(value)))

        return sqs


class ModelSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["models"] = forms.MultipleChoiceField(
            choices=model_choices(),
            required=False,
            label=_("Search In"),
            widget=forms.CheckboxSelectMultiple,
        )

    def get_models(self):
        """Return a list of the selected models."""
        search_models = []

        if self.is_valid():
            for model in self.cleaned_data["models"]:
                search_models.append(haystack_get_model(*model.split(".")))

        return search_models

    def search(self):
        sqs = super().search()
        return sqs.models(*self.get_models())


class HighlightedModelSearchForm(ModelSearchForm):
    def search(self):
        return super().search().highlight()


class FacetedModelSearchForm(ModelSearchForm):
    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)

    def search(self):
        sqs = super().search()

        if hasattr(self, "cleaned_data") and self.cleaned_data["selected_facets"]:
            sqs = sqs.narrow(self.cleaned_data["selected_facets"])

        return sqs.models(*self.get_models())
