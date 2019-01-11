from flask import current_app


class Reports:
    @classmethod
    def portfolio_totals(cls, portfolio):
        budget = current_app.csp.reports.get_budget(portfolio)
        spent = current_app.csp.reports.get_total_spending(portfolio)
        return {"budget": budget, "spent": spent}

    @classmethod
    def monthly_totals(cls, portfolio):
        return current_app.csp.reports.monthly_totals(portfolio)

    @classmethod
    def cumulative_budget(cls, portfolio):
        return current_app.csp.reports.cumulative_budget(portfolio)
