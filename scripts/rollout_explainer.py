import argparse
import json
import os
from pathlib import Path
from urllib import request, error


def create_evidence_summary(data):
    status = data["status"]
    version = data["version"]
    success_rate = data["metrics"]["success_rate_percent"]
    latency = data["metrics"]["p95_latency_seconds"]

    if status == "healthy":
        decision = "The rollout can continue."
    elif status == "paused":
        decision = "The rollout should remain paused for investigation."
    else:
        decision = "The rollout should be rolled back to the stable version."

    return "\n".join(
        [
            "# Canary Rollout Decision",
            "",
            f"**Version:** {version}",
            f"**Status:** {status}",
            f"**Success rate:** {success_rate}%",
            f"**P95 latency:** {latency} seconds",
            "",
            f"**Decision:** {decision}",
            "",
            (
                "The decision is based on the configured success-rate "
                "and latency thresholds."
            ),
        ]
    )


def build_ai_prompt(data):
    return f"""
You are a DevOps and Site Reliability assistant.

Explain why the following Kubernetes canary rollout succeeded,
paused, or rolled back.

Use only the supplied evidence.
Include the observed metrics, threshold comparison, operational
impact, and recommended next step.
Do not invent evidence or execute any deployment action.

Rollout evidence:

{json.dumps(data, indent=2)}
"""


def request_ai_explanation(prompt):
    api_key = os.getenv("AI_API_KEY")
    api_url = os.getenv(
        "AI_API_URL",
        "https://api.openai.com/v1/chat/completions",
    )
    model = os.getenv("AI_MODEL", "gpt-4o-mini")

    if not api_key:
        return None

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Provide evidence-based Kubernetes rollout explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
    }

    api_request = request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=60) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )
    except (error.HTTPError, error.URLError) as exc:
        raise RuntimeError(
            f"AI explanation request failed: {exc}"
        ) from exc

    return result["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(
        description="Explain Kubernetes canary rollout decisions."
    )
    parser.add_argument(
        "result",
        help="Path to rollout result JSON",
    )
    parser.add_argument(
        "--output",
        default="rollout-explanation.md",
    )
    args = parser.parse_args()

    result_path = Path(args.result)

    with result_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    summary = create_evidence_summary(data)
    ai_explanation = request_ai_explanation(
        build_ai_prompt(data)
    )

    if ai_explanation:
        summary += "\n\n## AI-Assisted Explanation\n\n"
        summary += ai_explanation

    Path(args.output).write_text(
        summary,
        encoding="utf-8",
    )

    print(summary)


if __name__ == "__main__":
    main()
