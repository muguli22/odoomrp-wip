# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class WizCreateFictitiousOf(models.TransientModel):
    _name = "wiz.create.fictitious.of"

    date_planned = fields.Datetime(
        string='Scheduled Date', required=True, default=fields.Datetime.now())
    load_on_product = fields.Boolean("Load cost on product")

    @api.multi
    def do_create_fictitious_of(self):
        production_obj = self.env['mrp.production']
        product_obj = self.env['product.product']
        self.ensure_one()
        active_ids = self.env.context['active_ids']
        active_model = self.env.context['active_model']
        production_list = []
        if active_model == 'product.template':
            cond = [('product_tmpl_id', 'in', active_ids)]
            product_list = product_obj.search(cond)
        else:
            product_list = product_obj.browse(active_ids)
        for product in product_list:
            vals = {'product_id': product.id,
                    'product_template': product.product_tmpl_id.id,
                    'product_qty': 1,
                    'date_planned': self.date_planned,
                    'user_id': self._uid,
                    'location_src_id': production_obj._src_id_default(),
                    'location_dest_id': production_obj._dest_id_default(),
                    'active': False,
                    'product_uom': product.uom_id.id
                    }
            new_production = production_obj.create(vals)
            production_list.append(new_production.id)
        if self.load_on_product:
            for production_id in production_list:
                try:
                    production = production_obj.browse(production_id)
                    production.action_compute()
                    production.calculate_production_estimated_cost()
                    production.load_product_std_price()
                except:
                    continue
        return {'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'domain': "[('id','in'," + str(production_list) + "), "
                "('active','=',False)]"
                }
