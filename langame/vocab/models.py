from django.db import models


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Language(models.TextChoices):
    EN = "en", "English"
    ZH = "zh", "Chinese"
    FI = "fi", "Finnish"


class Lexeme(models.Model):
    """
    某一种语言里的一个词/短语（可独立存在，可复用）
    例如: "apple"(en), "苹果"(zh), "omena"(fi)
    """
    language = models.CharField(max_length=2, choices=Language.choices, db_index=True)
    text = models.CharField(max_length=128, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["language", "text"], name="uniq_lexeme_lang_text")
        ]
        ordering = ["language", "text"]

    def __str__(self):
        return f"{self.text} ({self.language})"


class Term(models.Model):
    """
    一个“概念/词条”，用英文为主键式的主显示
    一个 Term 关联三个 Lexeme：en/zh/fi
    """
    en = models.ForeignKey(Lexeme, on_delete=models.PROTECT, related_name="term_en")
    zh = models.ForeignKey(Lexeme, on_delete=models.PROTECT, related_name="term_zh")
    fi = models.ForeignKey(Lexeme, on_delete=models.PROTECT, related_name="term_fi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["en", "zh", "fi"], name="uniq_term_triplet"),
        ]

    def __str__(self):
        return f"{self.en.text} / {self.zh.text} / {self.fi.text}"


