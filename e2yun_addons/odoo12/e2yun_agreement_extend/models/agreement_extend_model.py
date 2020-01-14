# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import datetime
class Agreement(models.Model):
    _inherit = "agreement"

    agreement_code=fields.Char('Agreement Code',default="/") #合同编码
    plan_sign_time=fields.Datetime('Plan Sign Time') # 计划回签时间


    @api.model
    def create(self, vals):
        vals['code'] = ""
        if 'agreement_subtype_id' in vals.keys() and vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])

          if agreement_subtype_obj.for_code and not (agreement_subtype_obj.name in '集团转包'
                                                     or agreement_subtype_obj.name in 'Other（其他）'):
            sequence_obj = self.env['ir.sequence']
            if 'agreement_type_id' in vals.keys():
                agreement_type_id=vals['agreement_type_id']
            else:
                agreement_type_id=self.agreement_type_id.id

            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two
                vals['code'] = vals['agreement_code']

        return super(Agreement, self).create(vals)

    def write(self, vals):
        if 'agreement_subtype_id' in vals.keys() and vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])

          if agreement_subtype_obj.for_code and not (agreement_subtype_obj.name in'集团转包'
                                                  or agreement_subtype_obj.name in '其他' ):
            sequence_obj = self.env['ir.sequence']
            if 'agreement_type_id' in vals.keys():
                agreement_type_id=vals['agreement_type_id']
            else:
                agreement_type_id=self.agreement_type_id.id

            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two
                vals['code'] = vals['agreement_code']
        return super(Agreement,self).write(vals)

    def send_approval_warn_emlil(self,interval_time):
        #mail.template / name_search
        #查找阶段为 待审批与审批中的数据
        agreement_obj=self.env['agreement']
        tier_review_obj = self.env['tier.review']
        agreement_datas = agreement_obj.search(
            [('stage_id', '<', 5)])
        day = datetime.timedelta(days=interval_time)
        for agreement_data in agreement_datas:
            tier_review_datas=tier_review_obj.search(
            [('res_id', '=', agreement_data.id)],  order="sequence asc" )
            i=0
            while i< len(tier_review_datas):
                tier_review_data=tier_review_datas[i]
                if tier_review_data.status!='approved':
                    if i==0:
                        now = datetime.datetime.now()
                        if (tier_review_data.write_date+day)<now:
                            partner_ids = []
                            if tier_review_data.w_approver_id:
                                partner_ids.append([6, False, tier_review_data.w_approver_id])
                                self.emil_temp(agreement_data.id,partner_ids)
                            else:
                                #审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_ids.append([6, False, agreement_data.assigned_user_id. sale_team_id.user_id.id])
                                    self.emil_temp(agreement_data.id, partner_ids)

                            break
                    else:
                        tier_review_data_temp = tier_review_datas[i-1]
                        now = datetime.datetime.now()
                        if (tier_review_data_temp.write_date + day) < now:
                            partner_ids = []
                            if tier_review_data.w_approver_id:
                                partner_ids.append([6, False, tier_review_data.w_approver_id])
                                self.emil_temp(agreement_data.id, partner_ids)
                            else:
                                # 审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_ids.append([6, False, agreement_data.assigned_user_id.sale_team_id.user_id.id])
                                    self.emil_temp(agreement_data.id, partner_ids)
                            break

                i=i+1

        #验证最后一次的审批时
        return  True
    def emil_temp(self,id,partner_ids,):
        ir_model_data = self.env['ir.model.data']
        template_ids = ir_model_data.get_object_reference('e2yun_agreement_extend', 'email_template_rocp_agreement')[1]
        email_template_obj_message = self.env['mail.compose.message']
        if template_ids:
            attachment_ids_value = email_template_obj_message.onchange_template_id(template_ids, 'comment',
                                                                                   'agreement', id)
            vals = {}
            vals['composition_mode'] = 'mass_mail'
            vals['template_id'] = template_ids
            vals['parent_id'] = False
            vals['notify'] = False
            vals['no_auto_thread'] = False
            vals['reply_to'] = False
            vals['model'] = 'agreement'
            vals['partner_ids'] =partner_ids
            vals['body'] = attachment_ids_value['value']['body']
            vals['res_id'] = id
            vals['email_from'] = attachment_ids_value['value']['email_from']
            vals['subject'] = attachment_ids_value['value']['subject']
            emil_id = self.env['mail.compose.message'].create(vals)
            emil_id.action_send_mail()


    def import_file(self):
        print(self.id)
        wizard = self.env.ref(
            'e2yun_agreement_extend.view_agreement_file_import')
        return {
            'name': '导入文件',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'agreement.file.upload',
            'views': [(wizard.id, 'form')],
            'view_id': wizard.id,
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }




class AgreementSubtype(models.Model):
    _inherit = "agreement.subtype"

    for_code = fields.Char(string="For Code", required=True)


class AgreementLine(models.Model):
    _inherit = "agreement.line"

    price_unit = fields.Float(string='单价', required=True)
    taxes_id = fields.Many2many('account.tax', string='税率', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Float(compute='_compute_amount', string='小计', store=True)



    @api.depends('qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:

            vals = line._prepare_compute_all_values()
            line.update({
                'price_subtotal': (vals['price_unit']*vals['qty'])-(vals['price_unit']*vals['qty']*vals['amount']),
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'qty': self.qty,
            'amount':self.taxes_id[0].amount/100,
        }
