permit (
principal,
action == ZeroTrustAgent::Action::"Read",
resource
) when {
principal.tenantId == resource.tenantId &&
principal.verified == true &&
principal.taskScope == "read_only" &&
principal.ephemeralTag != ""
};

forbid (
principal,
action == ZeroTrustAgent::Action::"Read",
resource
) when {
principal.tenantId != resource.tenantId
};
