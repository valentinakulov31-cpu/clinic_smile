class ActiveQuerysetMixin:
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        branch = self.request.query_params.get("branch")
        category = self.request.query_params.get("category")

        if branch and hasattr(queryset.model, "branches"):
            queryset = queryset.filter(branches__id=branch)
        if category and hasattr(queryset.model, "category_id"):
            queryset = queryset.filter(category__slug=category)

        return queryset.distinct()
