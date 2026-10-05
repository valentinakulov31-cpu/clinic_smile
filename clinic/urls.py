from django.urls import path

from . import views


urlpatterns = [
    path("branches/", views.BranchListView.as_view(), name="branch-list"),
    path("service-categories/", views.ServiceCategoryListView.as_view(), name="service-category-list"),
    path("services/", views.ServiceListView.as_view(), name="service-list"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service-detail"),
    path("prices/", views.PriceCategoryListView.as_view(), name="price-list"),
    path("offers/", views.OfferListView.as_view(), name="offer-list"),
    path("specialists/", views.SpecialistListView.as_view(), name="specialist-list"),
    path("specialist-categories/", views.SpecialistCategoryListView.as_view(), name="specialist-category-list"),
    path("specialists/<slug:slug>/", views.SpecialistDetailView.as_view(), name="specialist-detail"),
    path("patients-page/", views.PatientsPageView.as_view(), name="patients-page"),
    path("about/", views.AboutPageView.as_view(), name="about-page"),
    path("gallery/", views.GalleryListView.as_view(), name="gallery-list"),
    path("vacancies/", views.VacancyListView.as_view(), name="vacancy-list"),
    path("vacancies/<slug:slug>/", views.VacancyDetailView.as_view(), name="vacancy-detail"),
    path("contacts/", views.ContactInfoView.as_view(), name="contacts"),
    path("documents/", views.DocumentListView.as_view(), name="document-list"),
    path("document-categories/", views.DocumentCategoryListView.as_view(), name="document-category-list"),
    path("reviews/", views.ReviewListView.as_view(), name="review-list"),
    path("home/", views.HomePageView.as_view(), name="home-page"),
    path("advantages/", views.AdvantageListView.as_view(), name="advantage-list"),
    path("social-links/", views.SocialLinkListView.as_view(), name="social-link-list"),
    path("settings/", views.SiteSettingsView.as_view(), name="site-settings"),
    path("pages/", views.StaticPageListView.as_view(), name="static-page-list"),
    path("pages/<slug:key>/", views.StaticPageDetailView.as_view(), name="static-page-detail"),
]
