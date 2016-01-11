# -*- coding: utf-8 -*-
# © 2016 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, exceptions
from openerp.tools.translate import _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_move(self, quants, move, location_to, location_from=False,
                    lot_id=False, owner_id=False, src_package_id=False,
                    dest_package_id=False):
        """Refuse to move a blocked lot"""
        if lot_id:
            lot = self.env['stock.production.lot'].browse(lot_id)
            if lot.locked:
                raise exceptions.ValidationError(
                    _("The following lots/serial number is blocked and "
                      "cannot be moved:\n%s") % lot.name)
        super(StockQuant, self).quants_move(
            quants, move, location_to, location_from=location_from,
            lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id,
            dest_package_id=dest_package_id)
