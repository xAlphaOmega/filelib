# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

import requests

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def geo_find_bing(addr, apikey=False):
    if not addr:
        return None

    if not apikey:
        raise UserError(_('''API key for GeoCoding (Places) required.\n
                          Save this key in System Parameters with key: bing.api_key_geocode, value: <your api key>
                          Visit https://docs.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key
                          for more information.
                          '''))

    url = "https://dev.virtualearth.net/REST/v1/Locations/?"
    try:
        result = requests.get(url, params={'q':addr, 'o':'json', 'key':apikey}).json()
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

    if result['statusCode'] != 200:
        if result.get('statusDescription'):
            _logger.error(result['statusDescription'])
            error_msg = _('Unable to geolocate, received the error:\n%s'
                          '\n\nBing made this a paid feature.\n'
                          'You should first enable billing on your Bing account.\n'
                          'Then, go to Developer Console, and enable the APIs:\n'
                          'Geocoding, Maps Static, Maps Javascript.\n'
                          % result['statusDescription'])
            raise UserError(error_msg)

    try:
        if len(result['resourceSets']) > 0 and len(result['resourceSets'][0]) > 0:
            geo = result['resourceSets'][0]['resources'][0]['point']['coordinates']
            return float(geo[0]), float(geo[1])
        else:
            return None
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(
        field for field in [street, ("%s %s" % (zip or '', city or '')).strip(), state, country]
        if field
    ))


class ResPartner(models.Model):
    _inherit = "res.partner"

    # partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    # partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    # date_localization = fields.Date(string='Geolocation Date')

    @classmethod
    def _geo_localize(cls, apikey, street='', zip='', city='', state='', country=''):
        search = geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_find_bing(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find_bing(search, apikey)
        return result

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        apikey = self.env['ir.config_parameter'].sudo().get_param('bing.api_key_geocode',default='AqY4IFeQhJPHi5FjGBNc7hfgUNcaVf7S_qyyP_dlVCesSJUqI7dBA-gsyoAIUvGu')
        for partner in self.with_context(lang='en_US'):
            result = partner._geo_localize(apikey,
                                           partner.street,
                                           partner.zip,
                                           partner.city,
                                           partner.state_id.name,
                                           partner.country_id.name)
            if result:
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(partner)
                })
        return True
