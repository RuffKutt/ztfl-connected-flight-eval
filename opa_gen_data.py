import json, sys, random

n_tenants = int(sys.argv[1])
agents_per_tenant = int(sys.argv[2])
out_prefix = sys.argv[3]

random.seed(42)
tenants = [f"tenant-{i}" for i in range(n_tenants)]
agents = {}
services = {}
valid_agents = []

for t in tenants:
    for a in range(agents_per_tenant):
        aid = f"agent-{t}-{a}"
        agents[aid] = {"tenantId": t, "verified": True, "taskScope": "read_only", "ephemeralTag": f"tag-{aid}"}
        valid_agents.append((aid, t))

variant_tenants = tenants[:max(1, n_tenants // 10)] if n_tenants > 20 else tenants
for t in variant_tenants:
    agents[f"agent-{t}-unverified"] = {"tenantId": t, "verified": False, "taskScope": "read_only", "ephemeralTag": f"tag-{t}-unv"}
    agents[f"agent-{t}-wrongscope"] = {"tenantId": t, "verified": True, "taskScope": "write", "ephemeralTag": f"tag-{t}-ws"}
    agents[f"agent-{t}-notag"] = {"tenantId": t, "verified": True, "taskScope": "read_only", "ephemeralTag": ""}

for t in tenants:
    services[f"service-{t}"] = {"tenantId": t}

with open(f"{out_prefix}_data.json", "w") as f:
    json.dump({"agents": agents, "services": services}, f)

requests = []
for i in range(300):
    roll = random.random()
    if roll < 0.55:
        aid, atenant = random.choice(valid_agents)
        sid = f"service-{atenant}"
        expected = True
    elif roll < 0.70:
        aid, atenant = random.choice(valid_agents)
        other = [t for t in tenants if t != atenant]
        sid = f"service-{random.choice(other) if other else atenant}"
        expected = False
    elif roll < 0.80:
        t = random.choice(variant_tenants)
        aid, sid, expected = f"agent-{t}-unverified", f"service-{t}", False
    elif roll < 0.90:
        t = random.choice(variant_tenants)
        aid, sid, expected = f"agent-{t}-wrongscope", f"service-{t}", False
    else:
        t = random.choice(variant_tenants)
        aid, sid, expected = f"agent-{t}-notag", f"service-{t}", False
    requests.append({"agent_id": aid, "service_id": sid, "expected": expected})

with open(f"{out_prefix}_requests.json", "w") as f:
    json.dump(requests, f)

print(f"{out_prefix}: {len(agents)} agents, {len(services)} services")
