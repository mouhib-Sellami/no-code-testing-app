from django.contrib import admin

list_page = 20


class BaseModelAmin(admin.ModelAdmin):
    ordering = ['created_at']
    list_per_page = list_page

    def get_list_display(self, request):
        return self.list_display + ['created_at',
                                    'updated_at']
