from rest_framework import serializers
from .models import Term, Lexeme, Language


class LexemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lexeme
        fields = ["id", "language", "text"]


class TermSerializer(serializers.ModelSerializer):
    # 读：展开显示三种语言词
    en = LexemeSerializer(read_only=True)
    zh = LexemeSerializer(read_only=True)
    fi = LexemeSerializer(read_only=True)

    class Meta:
        model = Term
        fields = ["id", "en", "zh", "fi", "created_at", "updated_at"]


class TermCreateUpdateSerializer(serializers.ModelSerializer):
    """
    写：一次提交 en/zh/fi 的 text
    自动 get_or_create Lexeme，然后创建/更新 Term
    """
    en_text = serializers.CharField(max_length=128, write_only=True)
    zh_text = serializers.CharField(max_length=128, write_only=True)
    fi_text = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Term
        fields = ["id", "en_text", "zh_text", "fi_text"]

    def _get_or_create_lexeme(self, language, text, **extra):
        # 统一一下（英文建议小写存储；中文/芬兰语一般不需要）
        if language == Language.EN:
            text = text.strip()
        else:
            text = text.strip()

        lexeme, _ = Lexeme.objects.get_or_create(
            language=language,
            text=text,
            defaults=extra,
        )
        # 如果已存在，且你希望“补全空字段”，可以按需更新（可选）
        changed = False
        for k, v in extra.items():
            if v and not getattr(lexeme, k):
                setattr(lexeme, k, v)
                changed = True
        if changed:
            lexeme.save(update_fields=list(extra.keys()))
        return lexeme

    def create(self, validated_data):
        en_text = validated_data.pop("en_text")
        zh_text = validated_data.pop("zh_text")
        fi_text = validated_data.pop("fi_text")

        en = self._get_or_create_lexeme(Language.EN, en_text)
        zh = self._get_or_create_lexeme(Language.ZH, zh_text)
        fi = self._get_or_create_lexeme(Language.FI, fi_text)

        term = Term.objects.create(en=en, zh=zh, fi=fi)#, **validated_data)
        return term

    def update(self, instance, validated_data):

        # 如果你允许更新三种语言词条（可能会变成另一个 lexeme）
        if "en_text" in validated_data:
            en_text = validated_data.pop("en_text")
            instance.en = self._get_or_create_lexeme(Language.EN, en_text)

        if "zh_text" in validated_data:
            zh_text = validated_data.pop("zh_text")
            instance.zh = self._get_or_create_lexeme(Language.ZH, zh_text)

        if "fi_text" in validated_data:
            fi_text = validated_data.pop("fi_text")
            instance.fi = self._get_or_create_lexeme(Language.FI, fi_text)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance
