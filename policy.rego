package ztfl

default allow := false

allow if {
    agent := data.agents[input.agent_id]
    service := data.services[input.service_id]
    agent.tenantId == service.tenantId
    agent.verified == true
    agent.taskScope == "read_only"
    agent.ephemeralTag != ""
}
