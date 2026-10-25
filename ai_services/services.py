import json
import os

from openai import OpenAI
from pydantic import ValidationError

from .schemas import StoreContent


def generate_store_content(website):
    description = website.description.strip()

    if not description:
        raise ValueError("ابتدا توضیحات کسب‌وکار را وارد کنید.")

    api_key = os.getenv("GAPGPT_API_KEY")

    if not api_key:
        raise ValueError("کلید GAPGPT_API_KEY در فایل .env تنظیم نشده است.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.gapgpt.app/v1",
    )

    prompt = f"""
برای فروشگاه اینترنتی زیر، محتوای فارسی تولید کن.
خروجی فقط JSON معتبر باشد.

نام فروشگاه: {website.name}
نوع کسب‌وکار: {website.get_business_type_display()}
توضیحات: {description}

فیلدهای لازم:
title, description, welcome_message, about_us, categories, theme

برای theme از مقدار modern استفاده کن.
دسته‌بندی‌ها باید مرتبط با کسب‌وکار باشند.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "تو دستیار تولید محتوای فروشگاه اینترنتی هستی. "
                    "فقط JSON معتبر و بدون متن اضافی برگردان."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    raw_result = response.choices[0].message.content

    if not raw_result:
        raise ValueError("هوش مصنوعی پاسخ معتبری برنگرداند.")

    try:
        data = json.loads(raw_result)
        validated = StoreContent.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("ساختار پاسخ هوش مصنوعی معتبر نیست.") from exc

    return validated.model_dump()
