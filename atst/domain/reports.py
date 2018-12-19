from flask import current_app


class Reports:
    @classmethod
    def workspace_totals(cls, workspace):
        budget = current_app.csp.reports.get_budget(workspace)
        spent = current_app.csp.reports.get_total_spending(workspace)
        return {"budget": budget, "spent": spent}

    @classmethod
    def monthly_totals(cls, workspace):
        return current_app.csp.reports.monthly_totals(workspace)

    @classmethod
    def cumulative_budget(cls, workspace):
        return current_app.csp.reports.cumulative_budget(workspace)
