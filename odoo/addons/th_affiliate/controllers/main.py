# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import time

from werkzeug.exceptions import NotFound

from odoo import http, api
from odoo.http import request, Response
from odoo.addons.link_tracker.controller.main import LinkTracker
import json
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

date_format = '%m/%d/%Y, %I:%M:%S %p'
my_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Content-Type, Access-Control-Allow-Origin"
}


class ThLinkTracker(LinkTracker):
    @http.route('/api/check_cookie', type='http', auth='none')
    def check_cookie(self, **kwargs):
        setting = request.env['res.config.settings'].sudo().get_values()
        th_access_interval_number = setting.get('th_access_interval_number', False)
        th_access_interval_type = setting.get('th_access_interval_type', False)

        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Content-Type, Access-Control-Allow-Origin"
        }
        cookie = {
            'th_access_interval_number': th_access_interval_number,
            'th_access_interval_type': th_access_interval_type,

        }
        body = {'results': cookie}
        return Response(json.dumps(body), headers=headers)

    @http.route('/api/backlink', type='json', auth='none', cors='*', csrf=False, methods=["POST"])
    def back_link(self, **post):
        client_headers = request.httprequest.headers
        auth = client_headers.environ.get('HTTP_AUTHORIZATION', False)
        if auth:
            json_data = request.httprequest.data
            body_str = json_data.decode('utf-8')
            client_values = json.loads(body_str)
            get_link = client_values.get('link_tracker')
            th_website = client_headers.environ.get('HTTP_HOST')
            utm_params = client_values.get('odoo_utmParams', {})
            utm_source = utm_params.get('utm_source', '')
            utm_campaign = utm_params.get('utm_campaign', False)
            utm_medium = utm_params.get('utm_medium', False)
            referrer = client_values.get('referrer')
            code = client_values.get('code', False)

            domain = [('url', '=', get_link),
                      ('source_id.name', '=', utm_source)
                      ]
            if utm_campaign:
                domain.append(('campaign_id.name', '=', utm_campaign))
            else:
                domain.append(('campaign_id', '=', utm_campaign))

            if utm_medium:
                domain.append(('medium_id.name', '=', utm_medium))
            else:
                domain.append(('medium_id', '=', utm_medium))

            link_tracker = request.env['link.tracker'].sudo().search(domain)
            if link_tracker:
                vals = {
                    'th_count_link_click': int(link_tracker.th_count_link_click) + 1
                }
                if not link_tracker.th_count_link_ids or date.today() not in link_tracker.th_count_link_ids.mapped('th_date') \
                        or referrer not in link_tracker.th_count_link_ids.mapped('th_referrer'):
                    vals['th_count_link_ids'] = [(0, 0, {
                        'th_date': date.today(),
                        'th_click': 1,
                        'th_referrer': referrer
                    })]
                else:
                    th_count_link_id = link_tracker.th_count_link_ids.search([('th_date', '=', date.today()), ('th_referrer', '=', referrer)], limit=1, order='id desc')
                    th_count_link_id.th_click = th_count_link_id.th_click + 1
                link_tracker.sudo().write(vals)

                # test data
                # th_count_link_ids = link_tracker.th_count_link_ids.search([], limit=1, order='id desc')
                # vals['th_count_link_ids'] = [(0, 0, {
                #     'th_date': th_count_link_ids.th_date + timedelta(days=1),
                #     'th_click': th_count_link_ids.th_click + 1,
                #     'th_referrer': referrer
                # })]
                # link_tracker.sudo().write(vals)
            exist_user = request.env['th.session.user'].sudo().search([('th_user_client_code', '=', client_values.get('code'))])
            if not exist_user:
                create_user_click = request.env['th.session.user'].sudo().create({
                    'th_link_tracker_id': link_tracker.id if link_tracker else False,
                    'th_website': th_website,
                    'th_web_click_ids': [
                        (0, 0, {
                            'th_screen_time_start': datetime.now(),
                            'name': get_link,
                        })
                    ]
                })
            else:
                exist_user.write({'th_link_tracker_id': link_tracker.id if link_tracker else False})
                web_click_id = request.env['th.web.click'].sudo().search([('th_session_user_id', '=', exist_user.id)], order="id desc", limit=1)
                if web_click_id and web_click_id.name == get_link:
                    web_click_id.write({'th_screen_time_end': datetime.now()})
                else:
                    web_click_id.th_screen_time_end = datetime.now()
                    request.env['th.web.click'].sudo().create({
                        'th_screen_time_start': datetime.now(),
                        'name': get_link,
                        'th_session_user_id': exist_user.id
                    })

        try:
            body = {
                "Message": "Success",
                'code': create_user_click.th_user_client_code if create_user_click else exist_user.th_user_client_code,
                'status_code': 201
            }
            return body

        except Exception as e:
            response_data = {'Message': 'False', 'error': str(e)}
            return Response(json.dumps(response_data), status=500)

    # @http.route('/api/end_session', type='json', auth='none', cors='*', csrf=False, methods=["POST"])
    # def end_session(self):
    #     client_headers = request.httprequest.headers
    #     auth = client_headers.environ.get('HTTP_AUTHORIZATION', False)
    #     if auth:
    #         client_values = request.httprequest.get_json()
    #         get_link = client_values.get('code')
