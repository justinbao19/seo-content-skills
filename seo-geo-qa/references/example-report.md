# Illustrative QA report

This is a synthetic example to explain the schema, not a completed audit of a real article or customer.

```json
{
  "mode": "qa",
  "keyword": "model API guide",
  "verdict": "PASS",
  "critical_issues": {"seo_risks": [], "citation_risks": []},
  "warnings": {"seo_risks": ["FAQ count below 2"], "citation_risks": []},
  "llm_review_required": true,
  "llm_review_items": ["Verify H1 semantic intent matches target keyword"]
}
```

This PASS means no critical issue was found by the checks that ran. The reviewer still examines intent, evidence supporting the core claims, warnings and any missing coverage before issuing an editorial conclusion. A process exit code of 0 is not a PASS signal.

A dead reference or another configured critical issue produces FAIL in QA mode and REVISE in writer mode. Fix the specific issue, preserve the previous report, then review the newly generated report for the revised article. When the network is blocked, describe the limitation rather than reporting all checks as passed.
