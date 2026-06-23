from app.graph.state import MedicalState
from app.services.policy_service import determine_policy_mode


def policy_engine_node(state: MedicalState) -> dict:
    """
    策略决策中心。
    综合 triage_level 和 guardrail_result → 输出 policy_mode。
    policy_mode 控制 Answer 节点的回答模板、免责声明和转诊提示。
    """
    policy_mode = determine_policy_mode(
        triage_level=state.get("triage_level", "routine"),
        guardrail_result=state.get("guardrail_result", "pass"),
    )
    return {"policy_mode": policy_mode}
