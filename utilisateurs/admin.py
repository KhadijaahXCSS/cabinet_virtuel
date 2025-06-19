from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Docteur, Patient

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'nom', 'prenom', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'prenom')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Rôle', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'prenom', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('email',)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_nom', 'get_prenom', 'user_email')
    
    def get_nom(self, obj):
        return obj.user.nom
    get_nom.short_description = "Nom"
    
    def get_prenom(self, obj):
        return obj.user.prenom
    get_prenom.short_description = "Prénom"
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

class DocteurAdmin(admin.ModelAdmin):
    list_display = ('get_nom', 'get_prenom', 'specialite', 'user_email')
    
    def get_nom(self, obj):
        return obj.user.nom
    get_nom.short_description = "Nom"
    
    def get_prenom(self, obj):
        return obj.user.prenom
    get_prenom.short_description = "Prénom"
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

admin.site.register(User, CustomUserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Docteur, DocteurAdmin)