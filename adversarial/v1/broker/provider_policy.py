"""Fail-closed model-provider policy boundary, independent of any provider SDK.

No HTTP client, secrets, or remote calls in this module. A real provider
requires an explicit separately deployed adapter and operator configuration.
"""
from dataclasses import dataclass
from urllib.parse import urlsplit
import ipaddress

class ProviderPolicyError(ValueError):pass
@dataclass(frozen=True)
class ProviderPolicy:
    provider: str
    endpoint: str
    allowed_models: tuple[str,...]
    max_prompt_chars: int = 4096
    max_output_tokens: int = 512

def validate(policy:ProviderPolicy, model:str, prompt:str, requested_tokens:int):
    if not policy.provider or not policy.allowed_models:raise ProviderPolicyError('unconfigured_provider')
    url=urlsplit(policy.endpoint)
    if url.scheme!='https' or not url.hostname or url.username or url.password or url.fragment or url.query:
        raise ProviderPolicyError('endpoint_must_be_https_without_embedded_credentials')
    try:ipaddress.ip_address(url.hostname);raise ProviderPolicyError('ip_literal_not_allowed')
    except ValueError as exc:
        if isinstance(exc,ProviderPolicyError):raise
    if url.port not in (None,443):raise ProviderPolicyError('nonstandard_port')
    if model not in policy.allowed_models:raise ProviderPolicyError('model_not_allowlisted')
    if not isinstance(prompt,str) or len(prompt)>policy.max_prompt_chars:raise ProviderPolicyError('prompt_budget_exceeded')
    if type(requested_tokens) is not int or not 1<=requested_tokens<=policy.max_output_tokens:raise ProviderPolicyError('output_budget_exceeded')
    return {'provider':policy.provider,'host':url.hostname,'model':model,'max_output_tokens':requested_tokens,'status':'POLICY_ACCEPTED_NOT_EXECUTED'}