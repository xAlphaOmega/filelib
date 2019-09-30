# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, Warning
import suds.client

class e2yun_customer_payment_extend(models.Model):
    _inherit = 'account.payment'

    payment_type2 = fields.Selection(
        [('company_cash', '公司收现金'), ('credit_card', '刷卡'),
         ('company_wechat', '公司微信'), ('credit_alipay', '公司支付宝'),
         ('3rd_cash', '第三方现金'), ('3rd_card', '第三方刷卡'),
         ('3rd_check', '第三方支票'), ('3rd_ticket', '第三方优惠券'),
         ('3rd_wechat', '第三方微信'), ('3rd_alipay', '第三方支付宝'),
         ('3rd_eshop_o2o', '第三方电商O2O'), ('3rd_factory_o2o', '第三方厂家O2O'),
         ('eshop_alipay', '电商支付宝'), ('company_check', '公司收支票'),
         ('shop_cash', '门店现金'), ('transfer', '转账'), ('distributor_customized', '分销商定制货款')], '支付方式')
    currency = fields.Char('货币')
    payment_voucher =  fields.Char('付款凭证')
    marketing_activity = fields.Char('参与市场活动')
    bank_num = fields.Char('银行帐号')
    payment_attachments = fields.Many2many('ir.attachment', string="付款附件",
                                           domain=[('res_model', '=', 'account.payment')])

    related_shop = fields.Many2one('crm.team', '门店')
    receipt_Num = fields.Char('收据编号')
    sales_num = fields.Char('销售单号')
    handing_cost = fields.Float('手续费')
    po_num = fields.Char('市场合同号PO')
    customer_po = fields.Char('客户PO号')
    payment_status = fields.Selection([('A1', '定金'), ('A2', '中期款'),
                                       ('A3', '尾款'), ('A4', '全款')], '交款类型')
    payment_serirs_no = fields.Char('No.')

    def sync_customer_payment_to_pos(self):
        for r in self:
            if r.state == 'draft':
                raise exceptions.Warning('状态为草稿单据，不能同步到POS系统')

            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.sync_pos_payment_webservice_url')  # webservice调用地址
            client = suds.client.Client(url)

            result = client.service.createPayment(r.company_id.company_code,  # 公司
                                                 r.receipt_Num or '',  # 收款编号
                                                 r.company_id.name or '',  # 公司名称
                                                 r.po_num or '',  # PO
                                                 r.amount or '',  # 收款金额

                                                 '',  # 支票号
                                                 '',  # 销售单号
                                                 r.payment_voucher or '',  # 交款凭证
                                                 r.related_shop.shop_code,  # 门店
                                                 r.partner_id.name,  # 终端客户

                                                 '',  # 旺旺号
                                                 r.payment_date or '',  # 交款日期
                                                 r.handing_cost or '',  # 手续费
                                                 '',  # 货币
                                                 r.communication or '',  # 备注
                                                 r.marketing_activity or '',  # 参与市场活动
                                                 '',  # 到期日期

                                                 r.payment_type2 or '',  # 支付方式
                                                 r.payment_status or '',  # 交款类型
                                                 self.env.user.name,  # 经手人
                                                 r.sales_num or '',  # 收据单号
                                                 '',  # 支票状态
                                                 '',  # 收据日期
                                                 r.bank_num or '',  # 银行账户
                                                 r.customer_po,  # 客户PO

                                                 self.env.user.name,  # 创建人
                                                 self.create_date,  # 创建日期
                                                 )


    @api.model
    def create(self, vals_list):
        atch = vals_list['payment_attachments'] #[[6, false, [11077, 11022]]]
        temp = []
        for r in atch:  #[6,0,[11077]]
            if type(r) is list:

                for r1 in r:
                    if type(r1) is list:  #6, 0, [11077, 11022]
                        temp.extend(r1)

        for ids in temp:
            # atch_id = ids
            atch_line = self.env['ir.attachment'].browse(ids)
            atch_line.write({'res_model': 'account.payment'})

        res = super(e2yun_customer_payment_extend, self).create(vals_list)
        return res

    @api.one
    def write(self, vals):
        if vals.get('payment_attachments'):
            atch = vals['payment_attachments']
            temp = []
            for r in atch:
                if type(r) is list:

                    for r1 in r:
                        if type(r1) is list:
                            temp.extend(r1)

            for ids in temp:
                # atch_id = ids
                atch_line = self.env['ir.attachment'].browse(ids)
                atch_line.write({'res_model': 'account.payment'})
            return super(e2yun_customer_payment_extend, self).write(vals)
        else:
            return super(e2yun_customer_payment_extend, self).write(vals)

class e2yun_customer_payment_extend2(models.Model):
    _inherit = 'ir.attachment'

    @api.depends('datas')
    @api.onchange('datas')
    def _onchange_name(self):
        self.name = self.datas_fname
