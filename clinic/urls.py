from django.urls import path

from . import views


urlpatterns = [
    path("branches/", views.BranchListView.as_view(), name="branch-list"),
    path("service-categories/", views.ServiceCategoryListView.as_view(), name="service-category-list"),
    path("services/", views.ServiceListView.as_view(), name="service-list"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service-detail"),
    path("prices/", views.PriceCategoryListView.as_view(), name="price-list"),
    path("offers/", views.OfferListView.as_view(), name="offer-list"),
    path("offers/<slug:slug>/", views.OfferDetailView.as_view(), name="offer-detail"),
    path("specialists/", views.SpecialistListView.as_view(), name="specialist-list"),
    path("specialists/<slug:slug>/", views.SpecialistDetailView.as_view(), name="specialist-detail"),
    path("patients-page/", views.PatientsPageView.as_view(), name="patients-page"),
    path("about/", views.AboutPageView.as_view(), name="about-page"),
    path("gallery/", views.GalleryListView.as_view(), name="gallery-list"),
    path("vacancies/", views.VacancyListView.as_view(), name="vacancy-list"),
    path("vacancies/<slug:slug>/", views.VacancyDetailView.as_view(), name="vacancy-detail"),
    path("contacts/", views.ContactInfoView.as_view(), name="contacts"),
    path("documents/", views.DocumentListView.as_view(), name="document-list"),
    path("reviews/", views.ReviewListView.as_view(), name="review-list"),
]
