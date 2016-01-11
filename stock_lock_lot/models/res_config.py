# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockConfig(models.TransientModel):
    """Add an option for strict locking"""
    _inherit = 'stock.config.settings'

    module_stock_lock_lot_strict = fields.Boolean(
        string='Strictly forbid moves on blocked Serial Numbers/lots.',
        help="When this box is checked, users are not allowed to force the"
             "availability on blocked Serial Numbers/lots.")
