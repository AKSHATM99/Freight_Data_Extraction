from pathlib import Path
import json
from collections import defaultdict
from math import isclose

ground_truth_path = Path(__file__).parent / "files" / "ground_truth.json"
llm_output_path = Path(__file__).parent / "output.json"

with ground_truth_path.open() as f:
    ground_truth = json.load(f)

with llm_output_path.open() as f:
    llm_output = json.load(f)

gt_by_id = {item["id"]: item for item in ground_truth}
pred_by_id = {item["id"]: item for item in llm_output}

total_fields = 0
correct_fields = 0

field_stats = defaultdict(lambda: {"matched": 0, "total": 0})

for email_id, gt in gt_by_id.items():
    pred = pred_by_id.get(email_id, {})

    for key in gt:
        if key == "id":
            continue

        total_fields += 1
        field_stats[key]["total"] += 1

        pred_val = pred.get(key)
        gt_val = gt.get(key)

        if isinstance(pred_val, float) and isinstance(gt_val, float):
            if isclose(pred_val, gt_val, abs_tol=0.01):
                correct_fields += 1
                field_stats[key]["matched"] += 1
        else:
            if pred_val == gt_val:
                correct_fields += 1
                field_stats[key]["matched"] += 1

accuracy = round((correct_fields / total_fields) * 100, 2)

print("-------------------------")
print("Total Field Values:", total_fields)
print("Correct Field Values:", correct_fields)
print("Overall Accuracy:", accuracy, "%")
print("-------------------------")
print("Field Wise Accuracy:")
print("-------------------------")
for field, stats in field_stats.items():
    acc = round((stats["matched"] / stats["total"]) * 100, 2)
    print(f"{field}: {acc}%")
