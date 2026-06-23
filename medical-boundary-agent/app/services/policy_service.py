from typing import Dict

# policy_mode → 对应的回答约束规则
POLICY_RULES: Dict[str, Dict] = {
    "emergency": {
        "prefix": "⚠️ 紧急提示：请立即拨打 120 或前往最近急诊。\n\n",
        "suffix": "\n\n**重要：以上信息不能替代紧急医疗救治，请立即就医。**",
        "temperature": 0.1,
        "max_tokens": 512,
    },
    "advisory": {
        "prefix": "",
        "suffix": "\n\n*本回答仅供健康参考，不构成医疗诊断建议，具体情况请咨询专业医生。*",
        "temperature": 0.4,
        "max_tokens": 1024,
    },
    "referral": {
        "prefix": "",
        "suffix": "\n\n*您描述的情况建议前往正规医疗机构就诊，由专业医生面诊评估。*",
        "temperature": 0.3,
        "max_tokens": 768,
    },
    "blocked": {
        "prefix": "",
        "suffix": "",
        "temperature": 0.0,
        "max_tokens": 256,
    },
}


def get_policy_rules(policy_mode: str) -> Dict:
    return POLICY_RULES.get(policy_mode, POLICY_RULES["advisory"])


def determine_policy_mode(triage_level: str, guardrail_result: str) -> str:
    """
    根据 triage_level 和 guardrail_result 决定 policy_mode

    triage_level: "emergency" | "urgent" | "routine"
    guardrail_result: "pass" | "blocked"
    """
    if guardrail_result == "blocked":
        return "blocked"
    if triage_level == "emergency":
        return "emergency"
    if triage_level == "urgent":
        return "referral"
    return "advisory"
