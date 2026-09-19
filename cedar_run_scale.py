import json, subprocess, re, statistics, os, sys

CEDAR = "/home/claude/cedar-policy-cli-x86_64-unknown-linux-gnu/cedar"
os.makedirs("/tmp/ctxs2", exist_ok=True)
CTX = "/tmp/ctxs2/empty.json"
with open(CTX, "w") as f:
    f.write("{}")

def run_one(prefix, req):
    cmd = [
        CEDAR, "authorize",
        "--policies", "policies.cedar",
        "--schema", "schema.cedarschema",
        "--entities", f"{prefix}_entities.json",
        "--principal", f'ZeroTrustAgent::Agent::"{req["agent"]}"',
        "--action", 'ZeroTrustAgent::Action::"Read"',
        "--resource", f'ZeroTrustAgent::Service::"{req["service"]}"',
        "--context", CTX,
        "--timing",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout
    m = re.search(r"Authorization Time \(micro seconds\)\s*:\s*(\d+)", out)
    micros = int(m.group(1)) if m else None
    decision = "ALLOW" if "ALLOW" in out else ("DENY" if "DENY" in out else "ERROR")
    return micros, decision

prefix = sys.argv[1]
n = int(sys.argv[2])
with open(f"{prefix}_requests.json") as f:
    requests = json.load(f)[:n]
micros_list, correct, errors = [], 0, 0
for req in requests:
    micros, decision = run_one(prefix, req)
    if decision == "ERROR" or micros is None:
        errors += 1
        continue
    micros_list.append(micros)
    if decision == req["expected"]:
        correct += 1

s = sorted(micros_list)
out = dict(n=len(requests), errors=errors, correct=correct,
           mean=statistics.mean(s), p50=statistics.median(s),
           p95=s[int(len(s)*0.95)], p99=s[min(int(len(s)*0.99), len(s)-1)],
           min=min(s), max=max(s))
with open(f"{prefix}_result.json", "w") as f:
    json.dump(out, f, indent=2)
print(prefix, out)
