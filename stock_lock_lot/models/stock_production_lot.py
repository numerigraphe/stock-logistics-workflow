# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockProductionLot(models.Model):
    _name = 'stock.production.lot'
    _inherit = ['stock.production.lot', 'mail.thread']

    _mail_post_access = 'read'
    _track = {
        'locked': {
            'stock_lock_lot.mt_lock_lot': lambda self, cr, uid, obj,
            ctx=None: obj.locked,
            'stock_lock_lot.mt_unlock_lot': lambda self, cr, uid, obj,
            ctx=None: not obj.locked,
        },
    }

    def _get_product_locked(self, product):
        """Should create locked? (including categories and parents)

        @param product: browse-record for product.product
        @return True when the category of the product or one of the parents
                demand new lots to be locked"""
        _locked = product.categ_id.lot_default_locked
        categ = product.categ_id.parent_id
        while categ and not _locked:
            _locked = categ.lot_default_locked
            categ = categ.parent_id
        return _locked

    @api.one
    def _get_locked_value(self):
        return self._get_product_locked(self.product_id)

    locked = fields.Boolean(string='Blocked', default='_get_locked_value',
                            readonly=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        """Instruct the client to lock/unlock a lot on product change"""
        self.locked = self._get_product_locked(self.product_id)

    @api.multi
    def button_lock(self):
        """"Block the lot

        If the lot has reservations, they will be undone to lock the lot."""
        reserved_quants = self.env['stock.quant'].search(
            [('lot_id', 'in', self.ids),
             ('reservation_id', '!=', False),
             ('reservation_id.state', 'not in', ('cancel', 'done'))])
        reserved_quants.mapped("reservation_id").do_unreserve()
        # Block the lot
        return self.write({'locked': True})

    @api.multi
    def button_unlock(self):
        return self.write({'locked': False})

    # Kept in old API to maintain compatibility
    def create(self, cr, uid, vals, context=None):
        """Force the locking/unlocking, ignoring the value of 'locked'."""
        #  Web quick-create doesn't provide product_id in vals, but in context
        if context is None:
            context = {}
        product_id = vals.get('product_id', context.get('product_id', False))
        if product_id:
            vals['locked'] = self._get_product_locked(
                self.pool['product.product'].browse(
                    cr, uid, product_id, context=context))
        return super(StockProductionLot, self).create(
            cr, uid, vals, context=context)

    @api.multi
    def write(self, values):
        """"Lock the lot if changing the product and locking is required"""
        if 'product_id' in values:
            product = self.env['product.product'].browse(
                values.get('product_id'))
            values['locked'] = self._get_product_locked(product)
        return super(StockProductionLot, self).write(values)
