from flask import current_app
from itertools import groupby


class Reports:
    @classmethod
    def monthly_spending(cls, portfolio):
        return current_app.csp.reports.get_portfolio_monthly_spending(portfolio)

    @classmethod
    def expired_task_orders(cls, portfolio):
        return [
            task_order for task_order in portfolio.task_orders if task_order.is_expired
        ]

    @classmethod
    def obligated_funds_by_JEDI_clin(cls, portfolio):
        clin_spending = current_app.csp.reports.get_spending_by_JEDI_clin(portfolio)
        active_clins = portfolio.active_clins
        for jedi_clin, clins in groupby(
            active_clins, key=lambda clin: clin.jedi_clin_type
        ):
            if not clin_spending.get(jedi_clin.name):
                clin_spending[jedi_clin.name] = {}
            clin_spending[jedi_clin.name]["obligated"] = sum(
                clin.obligated_amount for clin in clins
            )
        return [
            {
                "name": clin,
                "invoiced": clin_spending[clin].get("invoiced", 0),
                "estimated": clin_spending[clin].get("estimated", 0),
                "obligated": clin_spending[clin].get("obligated", 0),
            }
            for clin in sorted(clin_spending.keys())
        ]
