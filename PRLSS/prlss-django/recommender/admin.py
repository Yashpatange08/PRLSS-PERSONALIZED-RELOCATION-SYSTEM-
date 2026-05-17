from django.contrib import admin
from django.utils.html import format_html
from .models import Apartment, TimelineVisit, UserPreference, RecommendationFeedback


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display  = ["name", "city", "rent_display", "college_dist", "amenity_score", "match_bar", "is_active"]
    list_filter   = ["city", "furnished", "bhk", "is_active"]
    search_fields = ["name", "address"]
    list_editable = ["is_active"]
    ordering      = ["city", "rent"]

    @admin.display(description="Rent")
    def rent_display(self, obj):
        return f"₹{obj.rent:,}"

    @admin.display(description="Match %")
    def match_bar(self, obj):
        pct   = obj.match_percent
        color = "#28a745" if pct >= 80 else "#ffc107" if pct >= 60 else "#dc3545"
        return format_html(
            '<div style="width:80px;background:#eee;border-radius:3px;">'
            '<div style="width:{}%;background:{};height:14px;border-radius:3px;'
            'text-align:center;color:white;font-size:10px;line-height:14px;">{}</div></div>',
            pct, color, f"{pct}%"
        )

    actions = ["mark_active", "mark_inactive"]

    @admin.action(description="Mark selected active")
    def mark_active(self, request, qs):
        qs.update(is_active=True)

    @admin.action(description="Mark selected inactive")
    def mark_inactive(self, request, qs):
        qs.update(is_active=False)


@admin.register(TimelineVisit)
class TimelineVisitAdmin(admin.ModelAdmin):
    list_display  = ["cluster_label_display", "lat", "lon", "visit_freq", "place_name"]
    list_filter   = ["cluster"]
    search_fields = ["place_name"]
    ordering      = ["-visit_freq"]

    @admin.display(description="Cluster")
    def cluster_label_display(self, obj):
        labels = {
            0: ("🎓", "College/Work", "#007bff"),
            1: ("🛒", "Market",       "#28a745"),
            2: ("🏠", "Home",         "#fd7e14"),
            3: ("🎭", "Leisure",      "#6f42c1"),
            4: ("🚉", "Transport",    "#20c997"),
        }
        icon, label, color = labels.get(obj.cluster, ("📍", f"Cluster {obj.cluster}", "#6c757d"))
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px;">'
            '{} {}</span>', color, icon, label
        )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display  = ["name", "mobile", "city", "rent_budget_display", "created_at"]
    list_filter   = ["city"]
    search_fields = ["name", "mobile"]
    readonly_fields = ["result_snapshot", "created_at"]

    @admin.display(description="Budget")
    def rent_budget_display(self, obj):
        return f"₹{obj.rent_budget:,}"


@admin.register(RecommendationFeedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display  = ["user_name", "apartment_name", "rating", "created_at"]
    list_filter   = ["rating"]
    search_fields = ["user_pref__name", "apartment__name"]

    @admin.display(description="User")
    def user_name(self, obj):
        return obj.user_pref.name

    @admin.display(description="Apartment")
    def apartment_name(self, obj):
        return obj.apartment.name
