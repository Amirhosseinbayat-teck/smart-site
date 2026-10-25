import os

from openai import OpenAI


def generate_product_description(
    product_name,
    category="",
    features="",
):
    if not product_name or not product_name.strip():
        raise ValueError("نام محصول را وارد کنید.")

    api_key = os.getenv("GAPGPT_API_KEY")

    if not api_key:
        raise ValueError("کلید GAPGPT_API_KEY تنظیم نشده است.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.gapgpt.app/v1",
    )

    prompt = f"""
برای محصول زیر، توضیحات جذاب و دقیق فارسی برای فروشگاه اینترنتی بنویس.

نام محصول: {product_name}
دسته‌بندی: {category}
ویژگی‌ها: {features}

قوانین:
- فقط متن توضیحات محصول را برگردان.
- متن روان، حرفه‌ای و مناسب فروشگاه اینترنتی باشد.
- اطلاعات و ویژگی‌های تأییدنشده را اختراع نکن.
- از مقدمه و توضیحات اضافی خودداری کن.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "تو نویسنده حرفه‌ای توضیحات محصولات فروشگاه اینترنتی "
                    "به زبان فارسی هستی."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )

    description = response.choices[0].message.content

    if not description or not description.strip():
        raise ValueError("هوش مصنوعی توضیحات معتبری تولید نکرد.")

    return description.strip()