# bbbn
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_bank_statements_reconciled = fields.Boolean(
        'Bank Statement Reconciled', compute='_is_bank_statements_reconciled',)

    def _is_bank_statements_reconciled(self):
        for move in self:
            if move.matched_payment_ids and move.matched_payment_ids.reconciled_statement_line_ids:
                if False not in move.matched_payment_ids.reconciled_statement_line_ids.mapped(
                        'is_reconciled'):
                    total_reconciled_amount = sum(
                        move.matched_payment_ids.reconciled_statement_line_ids.mapped('amount'))
                    if move.amount_total == total_reconciled_amount:
                        move.is_bank_statements_reconciled = True
                    else:
                        move.is_bank_statements_reconciled = False
                else:
                    move.is_bank_statements_reconciled = False
            else:
                move.is_bank_statements_reconciled = False
