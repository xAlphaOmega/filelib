# -*- coding: utf-8 -*-
from _datetime import datetime

from odoo import api, fields, models, exceptions, tools


class OutboundFinal(models.Model):
    _name = 'outbound.final'
    _description = '出库报表'

    def default_werks(self):
        return self.env['res.company']._company_default_get('outbound.final').company_code

    def default_werks_id(self):
        return self.env['res.company']._company_default_get('outbound.final').id

    ID = fields.Char('ID')
    salesorderid = fields.Char('销售订单')
    LFADT = fields.Datetime('日期')
    start_date = fields.Datetime('日期从')
    end_date = fields.Datetime('日期到')
    werks = fields.Char('工厂', default=default_werks, readonly=True)
    werks_id = fields.Integer('工厂', default=default_werks_id, readonly=True)
    vkorgtext = fields.Char('事业部')
    vtweg = fields.Char('分销渠道')
    ywy = fields.Char('导购员')
    # mendian = fields.Char('门店编码')
    kunnr = fields.Many2one('crm.team', '门店')
    # jine = fields.Char('金额')
    jiesuanjine = fields.Char('结算小计')
    xiaoshoujine = fields.Char('销售小计')

    def init_date(self, ctx):

        start_date = ctx['start_date']
        end_date = ctx['end_date']
        LFADT_sql = "upper('LFADT') between '%s' and '%s'" % (start_date, end_date)
        if ctx['werks']:
            werks_sql = "and werks = '%s'" % ctx['werks']
        else:
            werks_sql = ""
        if ctx['vtweg']:
            vtweg_sql = "and vtweg = %s" % ctx['vtweg']
        else:
            vtweg_sql = ""
        if ctx['vkorgtext']:
            vkorgtext_sql = "and vkorgtext = %s" % ctx['vkorgtext']
        else:
            vkorgtext_sql = ""
        if ctx['kunnr']:
            kunnr_sql = "and kunnr = %s" % int(ctx['kunnr'][0])
        else:
            kunnr_sql = ""
        if ctx['ywy']:
            ywy_sql = "and ywy = %s" % ctx['ywy']
        else:
            ywy_sql = ""

        sql_str = "select * from outbound_final where %s %s %s %s %s" % (LFADT_sql, vtweg_sql, vkorgtext_sql, kunnr_sql, ywy_sql)

        self._cr.execute(sql_str)

    def open_table(self):
        data = self.read()[0]
        ctx = self._context.copy()

        if data['start_date'] and data['end_date']:
            if data['start_date'] > datetime.now():
                raise exceptions.Warning('开始日期不能大于当前日期')
            elif data['start_date'] > data['end_date']:
                raise exceptions.Warning('开始日期不能大于结束日期')
            elif data['end_date'] > datetime.now():
                raise exceptions.Warning('结束日期不能大于当前日期')
            ctx['start_date'] = data['start_date']
            ctx['end_date'] = data['end_date']
        else:
            raise exceptions.Warning('查询日期不能为空')

        ctx['werks'] = data['werks']
        ctx['vtweg'] = data['vtweg']
        ctx['vkorgtext'] = data['vkorgtext']
        ctx['kunnr'] = data['kunnr']
        ctx['ywy'] = data['ywy']

        self.init_date(ctx)

        return {
            'name': '出库报表查询',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'outbound.final',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def search(self, args, offset=0, limit=None, order=None, count=False):
        domain_list = []
        sql1 = ('LFADT', '>=', self._context['start_date'])
        sql2 = ('LFADT', '<=', self._context['end_date'])
        domain_list.append(sql1)
        domain_list.append(sql2)
        if self._context['werks']:
            werks_query = ('werks', '=', self._context['werks'])
            domain_list.append(werks_query)
        if self._context['vtweg']:
            vtweg_query = ('vtweg', '=', self._context['vtweg'])
            domain_list.append(vtweg_query)
        if self._context['vkorgtext']:
            vkorgtext_query = ('vkorgtext', '=', self._context['vkorgtext'])
            domain_list.append(vkorgtext_query)
        if self._context['kunnr']:
            kunnr_query = ('kunnr', '=', self._context['kunnr'][0])
            domain_list.append(kunnr_query)
        if self._context['ywy']:
            ywy_query = ('ywy', '=', self._context['ywy'])
            domain_list.append(ywy_query)

        args = args + domain_list
        return super(OutboundFinal, self).search(
            args, offset=offset, limit=limit, order=order,
            count=count)
