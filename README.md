# ZTFL Quantitative Evaluation - Reproducibility Package

Tools used (official releases, not reimplementations):
- Cedar CLI v4.13.0: https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.13.0
- OPA v1.20.2: https://github.com/open-policy-agent/opa/releases/tag/v1.20.2

## Cedar benchmark
1. `python3 gen_entities2.py <n_tenants> <agents_per_tenant> <prefix>` generates entities/requests
2. `python3 cedar_run_scale.py <prefix> <n_requests>` runs the benchmark, writes `<prefix>_result.json`
   (requires `cedar` binary path set at top of script)

## OPA benchmark
1. `python3 opa_gen_data.py <n_tenants> <agents_per_tenant> <prefix>` generates data/requests
2. `python3 run_opa_bench.py <prefix> <agent_id> <service_id>` runs OPA's native bench harness
   (requires `opa` binary path set at top of script)

## Policy files
- `schema.cedarschema` / `policies.cedar`: exact Cedar policy from Section V of the paper
- `policy.rego`: logically identical policy reimplemented in Rego for Section VI-B comparison

## Scales tested
70-100, 1,130-1,230, 10,650-11,150, and 52,600-54,600 entities, corresponding to
10, 100, 500, and 2,000 tenants respectively.
