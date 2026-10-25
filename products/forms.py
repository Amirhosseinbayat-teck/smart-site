

from django import forms

from ai_services.product_description_service import (
    generate_product_description,
)
from .models import Product


class ProductAdminForm(forms.ModelForm):
    generate_ai_description = forms.BooleanField(
        label="تولید توضیحات با هوش مصنوعی",
        required=False,
    )

    ai_features = forms.CharField(
        label="ویژگی‌های محصول برای هوش مصنوعی",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("generate_ai_description"):
            name = cleaned_data.get("name", "")
            category = cleaned_data.get("category")
            features = cleaned_data.get("ai_features", "")

            if not name.strip():
                raise forms.ValidationError(
                    "ابتدا نام محصول را وارد کنید."
                )

            try:
                description = generate_product_description(
                    product_name=name,
                    category=category.name if category else "",
                    features=features,
                )
            except Exception as exc:
                raise forms.ValidationError(
                    f"تولید توضیحات ناموفق بود: {exc}"
                ) from exc

            cleaned_data["description"] = description

        return cleaned_data