import subprocess, json, sys

scale = sys.argv[1]
agent_id = sys.argv[2]
service_id = sys.argv[3]
count = sys.argv[4] if len(sys.argv) > 4 else "1"

with open(f"/tmp/bench_in_{scale}.json", "w") as f:
    json.dump({"agent_id": agent_id, "service_id": service_id}, f)

cmd = ["/home/claude/opa", "bench", "-d", "policy.rego", "-d", f"{scale}_data.json",
       "-i", f"/tmp/bench_in_{scale}.json", "data.ztfl.allow", "--count", count, "-f", "json"]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
# opa bench with json format streams one JSON object per line/block; take the last complete one
text = result.stdout.strip()
# find last top-level JSON object
depth = 0
last_start = None
objs = []
start = None
for i, ch in enumerate(text):
    if ch == '{':
        if depth == 0:
            start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and start is not None:
            objs.append(text[start:i+1])
data = json.loads(objs[-1])
mean_ns = data["Extra"]["histogram_timer_rego_query_eval_ns_mean"]
median_ns = data["Extra"]["histogram_timer_rego_query_eval_ns_median"]
p95 = data["Extra"]["histogram_timer_rego_query_eval_ns_95%"]
p99 = data["Extra"]["histogram_timer_rego_query_eval_ns_99%"]
print(f"{scale}: N={data['N']} mean={mean_ns/1000:.2f}us median={median_ns/1000:.2f}us p95={p95/1000:.2f}us p99={p99/1000:.2f}us")
