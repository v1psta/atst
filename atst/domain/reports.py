from flask import current_app


class Reports:
    @classmethod
    def monthly_totals(cls, portfolio):
        return current_app.csp.reports.monthly_totals(portfolio)

    @classmethod
    def expired_task_orders(cls, portfolio):
        return current_app.csp.reports.get_expired_task_orders(portfolio)

    @classmethod
    def obligated_funds_by_JEDI_clin(cls, portfolio):
        return current_app.csp.reports.get_obligated_funds_by_JEDI_clin(portfolio)
