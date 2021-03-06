from atst.domain.csp.policy import AzurePolicyManager, AzurePolicy


def test_portfolio_definitions():
    manager = AzurePolicyManager("policies")
    assert len(manager.portfolio_definitions) > 0
    policy = manager.portfolio_definitions[0]
    assert isinstance(policy, AzurePolicy)
