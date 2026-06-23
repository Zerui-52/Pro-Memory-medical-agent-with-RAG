from typing import List


_CATEGORY_KEYWORDS = {
    "症状": ["症状", "疼痛", "发烧", "咳嗽", "头痛", "呕吐", "腹泻"],
    "疾病": ["疾病", "病", "诊断", "确诊", "慢性", "急性"],
    "用药": ["药", "剂量", "服用", "处方", "副作用"],
    "检查": ["检查", "化验", "CT", "MRI", "血常规", "B超"],
}


def tag_filter(query: str) -> List[str]:
    q = query.lower()
    matched = [cat for cat, kws in _CATEGORY_KEYWORDS.items() if any(kw in q for kw in kws)]
    return matched if matched else ["default"]
