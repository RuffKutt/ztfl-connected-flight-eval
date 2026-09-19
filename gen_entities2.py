import json, sys, random

n_tenants = int(sys.argv[1])
agents_per_tenant = int(sys.argv[2])
out_prefix = sys.argv[3]

random.seed(42)
entities = []
tenants = [f"tenant-{i}" for i in range(n_tenants)]

for t in tenants:
    entities.append({"uid": {"type": "ZeroTrustAgent::Tenant", "id": t}, "attrs": {}, "parents": []})

valid_agents = []
for t in tenants:
    for a in range(agents_per_tenant):
        aid = f"agent-{t}-{a}"
        valid_agents.append((aid, t))
        entities.append({
            "uid": {"type": "ZeroTrustAgent::Agent", "id": aid},
            "attrs": {"tenantId": t, "verified": True, "taskScope": "read_only", "ephemeralTag": f"tag-{aid}"},
            "parents": [{"type": "ZeroTrustAgent::Tenant", "id": t}]
        })
    # one pre-baked variant agent per failure mode, per tenant (first N tenants only, to keep file size sane)
    if tenants.index(t) < max(1, n_tenants // 10) or n_tenants <= 20:
        entities.append({
            "uid": {"type": "ZeroTrustAgent::Agent", "id": f"agent-{t}-unverified"},
            "attrs": {"tenantId": t, "verified": False, "taskScope": "read_only", "ephemeralTag": f"tag-{t}-unv"},
            "parents": [{"type": "ZeroTrustAgent::Tenant", "id": t}]
        })
        entities.append({
            "uid": {"type": "ZeroTrustAgent::Agent", "id": f"agent-{t}-wrongscope"},
            "attrs": {"tenantId": t, "verified": True, "taskScope": "write", "ephemeralTag": f"tag-{t}-ws"},
            "parents": [{"type": "ZeroTrustAgent::Tenant", "id": t}]
        })
        entities.append({
            "uid": {"type": "ZeroTrustAgent::Agent", "id": f"agent-{t}-notag"},
            "attrs": {"tenantId": t, "verified": True, "taskScope": "read_only", "ephemeralTag": ""},
            "parents": [{"type": "ZeroTrustAgent::Tenant", "id": t}]
        })

services = []
for t in tenants:
    sid = f"service-{t}"
    services.append((sid, t))
    entities.append({
        "uid": {"type": "ZeroTrustAgent::Service", "id": sid},
        "attrs": {"tenantId": t},
        "parents": [{"type": "ZeroTrustAgent::Tenant", "id": t}]
    })

with open(f"{out_prefix}_entities.json", "w") as f:
    json.dump(entities, f)

variant_tenants = tenants[:max(1, n_tenants // 10)] if n_tenants > 20 else tenants

requests = []
for i in range(2000):
    roll = random.random()
    if roll < 0.55:
        aid, atenant = random.choice(valid_agents)
        sid, stenant = random.choice([s for s in services if s[1] == atenant])
        expected = "ALLOW"
    elif roll < 0.70:
        aid, atenant = random.choice(valid_agents)
        sid, stenant = random.choice([s for s in services if s[1] != atenant] or services)
        expected = "DENY"
    elif roll < 0.80:
        t = random.choice(variant_tenants)
        aid = f"agent-{t}-unverified"
        sid = f"service-{t}"
        expected = "DENY"
    elif roll < 0.90:
        t = random.choice(variant_tenants)
        aid = f"agent-{t}-wrongscope"
        sid = f"service-{t}"
        expected = "DENY"
    else:
        t = random.choice(variant_tenants)
        aid = f"agent-{t}-notag"
        sid = f"service-{t}"
        expected = "DENY"
    requests.append({"agent": aid, "service": sid, "expected": expected})

with open(f"{out_prefix}_requests.json", "w") as f:
    json.dump(requests, f)

print(f"{out_prefix}: {len(entities)} entities, {len(requests)} requests")
