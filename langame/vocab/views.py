from django.shortcuts import render


import random
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Term
from .serializers import TermSerializer, TermCreateUpdateSerializer


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.select_related("en", "zh", "fi").all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return TermCreateUpdateSerializer
        return TermSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # 简单搜索：q=apple 或 q=苹果 或 q=omena
        q = self.request.query_params.get("q")
        if q:
            q = q.strip()
            qs = qs.filter(
                Q(en__text__icontains=q) |
                Q(zh__text__icontains=q) |
                Q(fi__text__icontains=q)
            )

        return qs.distinct()

    @action(detail=False, methods=["get"])
    def game_pairs(self, request):
        """
        生成匹配游戏数据：
        - count: 抽多少个词条
        - langs: 选择两种语言，如 langs=en,zh / langs=en,fi / langs=zh,fi
                 不传就随机选两种
        返回：
        {
          "langs": ["en","zh"],
          "left": [{"id": 1, "text": "apple"}, ...],
          "right": [{"id": 1, "text": "苹果"}, ...]  # 同 id 表示正确配对（但顺序会被打乱）
        }
        """
        count = int(request.query_params.get("count", "10"))
        langs_param = request.query_params.get("langs")

        all_lang_pairs = [("en", "zh"), ("en", "fi"), ("zh", "fi")]
        if langs_param:
            parts = [p.strip() for p in langs_param.split(",") if p.strip()]
            if len(parts) == 2 and tuple(parts) in all_lang_pairs:
                a, b = parts
            else:
                a, b = random.choice(all_lang_pairs)
        else:
            a, b = random.choice(all_lang_pairs)

        # 这里用 order_by("?") 简单但大表性能一般；后面可以换更高效的随机策略
        terms = list(self.get_queryset().order_by("?")[:count])

        def pick_text(term, lang):
            if lang == "en":
                return term.en.text
            if lang == "zh":
                return term.zh.text
            return term.fi.text

        left = [{"id": t.id, "text": pick_text(t, a)} for t in terms]
        right = [{"id": t.id, "text": pick_text(t, b)} for t in terms]
        random.shuffle(right)

        return Response({"langs": [a, b], "left": left, "right": right})
