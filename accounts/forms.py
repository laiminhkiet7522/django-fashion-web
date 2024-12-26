from django import forms
from .models import Account
import re


class RegistrationForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        self.validate_email(cleaned_data.get("email"))
        self.validate_phone_number(cleaned_data.get("phone_number"))
        self.validate_passwords(
            cleaned_data.get("password"),
            cleaned_data.get("confirm_password"),
        )
        return cleaned_data

    def validate_email(self, email):
        """
        Kiểm tra email đã tồn tại hay chưa.
        """
        if Account.objects.filter(email=email).exists():
            self.add_error(
                "email", "Email này đã được sử dụng, vui lòng chọn email khác."
            )

    def validate_phone_number(self, phone_number):
        """
        Kiểm tra số điện thoại có hợp lệ hay không.
        """
        valid_prefixes = [
            "086",
            "096",
            "097",
            "098",
            "032",
            "033",
            "034",
            "035",
            "036",
            "037",
            "038",
            "039",  # Viettel
            "088",
            "091",
            "094",
            "083",
            "084",
            "085",
            "081",
            "082",  # Vinaphone
            "089",
            "090",
            "093",
            "070",
            "079",
            "077",
            "076",
            "078",  # Mobifone
        ]

        if not re.match(r"^\d{10}$", phone_number):
            self.add_error("phone_number", "Số điện thoại phải đúng 10 chữ số.")
            return

        if phone_number[:3] not in valid_prefixes:
            self.add_error(
                "phone_number", "Số điện thoại không hợp lệ với nhà mạng tại Việt Nam."
            )

    def validate_passwords(self, password, confirm_password):
        """
        Kiểm tra độ dài mật khẩu; sự khớp giữa mật khẩu và mật khẩu xác nhận.
        """
        if not password or len(password) < 6:
            self.add_error("password", "Mật khẩu phải dài ít nhất 6 ký tự.")
        if password != confirm_password:
            self.add_error("confirm_password", "Hai mật khẩu bạn nhập không khớp nhau.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Định nghĩa thuộc tính placeholder cho các trường
        self.fields["first_name"].widget.attrs[
            "placeholder"
        ] = "Nhập vào họ và tên đệm . . ."
        self.fields["last_name"].widget.attrs["placeholder"] = "Nhập vào tên . . ."
        self.fields["phone_number"].widget.attrs[
            "placeholder"
        ] = "Nhập vào số điện thoại . . ."
        self.fields["email"].widget.attrs["placeholder"] = "Nhập vào email . . ."
        self.fields["password"] = forms.CharField(
            widget=forms.PasswordInput(attrs={"placeholder": "Nhập vào mật khẩu . . ."})
        )
        self.fields["confirm_password"] = forms.CharField(
            widget=forms.PasswordInput(attrs={"placeholder": "Nhập lại mật khẩu . . ."})
        )

        # Gán class="form-control" cho tất cả các trường
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
