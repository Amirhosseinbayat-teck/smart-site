from django import forms


class HomepageEditForm(forms.Form):
    title = forms.CharField(
        label="عنوان فروشگاه",
        max_length=150,
    )
    welcome_message = forms.CharField(
        label="پیام خوشامدگویی",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    description = forms.CharField(
        label="توضیحات صفحه اصلی",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    about_us = forms.CharField(
        label="درباره فروشگاه",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    categories = forms.CharField(
        label="دسته‌بندی‌ها (هر دسته در یک خط)",
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    theme = forms.ChoiceField(
        label="قالب ظاهری",
        choices=[
            ("modern", "مدرن"),
        ],
    )

    def clean_categories(self):
        value = self.cleaned_data["categories"]
        categories = [
            item.strip()
            for item in value.splitlines()
            if item.strip()
        ]

        if not categories:
            raise forms.ValidationError(
                "حداقل یک دسته‌بندی وارد کنید."
            )

        return categories