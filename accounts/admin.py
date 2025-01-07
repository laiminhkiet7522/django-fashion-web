from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile

# Register your models here.


class AccountAdmin(UserAdmin):
    # Xác định các cột hiển thị trong danh sách các đối tượng Account ở giao diện Admin.
    list_display = ('email', 'first_name', 'last_name',
                    'username', 'last_login', 'date_joined', 'is_active')

    # Chỉ định các trường được liên kết để dẫn đến trang chi tiết đối tượng.
    list_display_links = ('email', 'first_name', 'last_name')

    # Định nghĩa các trường chỉ được xem, không thể chỉnh sửa trong giao diện Admin
    readonly_fields = ('last_login', 'date_joined')

    # Xác định thứ tự sắp xếp danh sách.
    ordering = ('-date_joined',)

    # Dùng để hiển thị các trường nhiều lựa chọn(ManyToManyField) trong giao diện Admin dưới dạng danh sách kéo thả
    filter_horizontal = ()

    # Dùng để thêm bộ lọc trong giao diện Admin(theo các trường nhất định)
    list_filter = ()

    # Dùng để nhóm các trường trong trang chi tiết của một đối tượng
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "commune", "district", "city")


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
