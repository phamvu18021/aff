# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

import json
import logging
from datetime import datetime
from odoo import http, fields
from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request, Response
_logger = logging.getLogger(__name__)


class LinkTrackerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'get_link_seeding' in counters:
            domain = [
                ('campaign_id.th_start_date', '<=', datetime.today().date()),
                ('campaign_id.th_end_date', '>=', datetime.today().date())
            ]
            values['get_link_seeding'] = (
                str(request.env['th.link.seeding'].sudo().search_count(domain)))

        if 'own_link_tracker' in counters:
            domain = [('th_aff_partner_id.id', '=', request.env.user.partner_id.id)]
            values['own_link_tracker'] = (
                str(request.env['link.tracker'].sudo().search_count(domain)))

        if 'link_outside_view' in counters:
            domain = [('th_aff_partner_id.id', '=', request.env.user.partner_id.id)]
            values['link_outside_view'] = (
                str(request.env['link.tracker'].sudo().search_count(domain)))

        return values

    # link seeding
    @http.route(['/my/seeding_partner'], type='http', auth="user", website=True)
    def seeding_partner(self, **kwargs):
        values = {
            'page_name': 'seeding_partner',
        }

        return request.render("th_affiliate.th_seeding_partner", values)

    @http.route(['/my/get_link_seeding', '/my/get_link_seeding/page/<int:page>'], type='http', auth="user",
                website=True)
    def list_get_link_seeding(self, page=1, sortby='id', search='', search_in="All", **kwargs):
        domain = [
            ('campaign_id.th_start_date', '<=', datetime.today().date()),
            ('campaign_id.th_end_date', '>=', datetime.today().date())
        ]
        th_link_seeding = request.env['th.link.seeding']
        total_links = th_link_seeding.sudo().search_count(domain)
        page_detail = pager(url='/my/get_link',
                            total=total_links,
                            page=page,
                            step=10)
        link_seeds = th_link_seeding.sudo().search(domain, limit=10, offset=page_detail['offset'], order='id desc')
        form_exist = request.env['link.tracker'].search([])

        values = {
            'link_seeds': link_seeds,
            'page_name': 'get_list_link_seeding',
            'pager': page_detail,
            # 'form_exist': form_exist
        }
        return request.render("th_affiliate.th_list_get_link_seeding", values)

    @http.route(['/my/create_link_tracker/<model("th.link.seeding"):link_id>'], type='http', auth="user", website=True)
    def form_create_link_tracker(self, link_id, **kwargs):

        user_id = request.env.user.id
        contact_affiliate = request.env['res.partner'].sudo().search([('user_ids.id', '=', user_id)], limit=1)
        domain = [
            ('th_link_seeding_id', '=', link_id.id),
            ('th_aff_partner_id', '=', contact_affiliate.id),
            ('campaign_id', '=', link_id.sudo().campaign_id.id),
            ('medium_id', '=', link_id.sudo().medium_id.id)
        ]

        link_exit = request.env['link.tracker'].sudo().search(domain)
        if not link_exit:
            create_link = request.env['th.link.seeding'].action_create_link_tracker(user_id, link_origin=link_id)
        value = link_exit if link_exit else create_link
        values = {'link_tracker': value, 'page_name': 'create_link'}
        return request.render("th_affiliate.th_own_link_seeding", values)

    # link tracker
    @http.route(['/my/own_link_tracker', '/my/own_link_tracker/page/<int:page>'], type='http', auth="user",
                website=True)
    def list_own_link_tracker(self, page=1, sortby='id', search='', search_in="All", **kwargs):
        domain = [('th_aff_partner_id.id', '=', request.env.user.partner_id.id)]
        th_link_tracker = request.env['link.tracker']
        total_links = th_link_tracker.sudo().search_count(domain)
        page_detail = pager(url='/my/get_link',
                            total=total_links,
                            page=page,
                            step=10)
        link_seeds = th_link_tracker.sudo().search(domain, limit=10, offset=page_detail['offset'], order='id desc')
        values = {
            'link_tracker': link_seeds,
            'page_name': 'own_links',
            'pager': page_detail,
        }
        return request.render("th_affiliate.th_list_own_link_tracker", values)

    @http.route(['/my/info_link/<model("link.tracker"):link_tracker_id>'], type='http', auth="user", website=True)
    def form_info_link(self, link_tracker_id, **kwargs):
        values = {'link_tracker': link_tracker_id, 'page_name': 'own_link_info'}
        return request.render("th_affiliate.th_own_link_seeding", values)

    # post link
    @http.route('/my/get_post_link/<model("link.tracker"):link_tracker_id>', type='http', auth="public",
                methods=['GET'], website=True)
    def get_post_link(self, link_tracker_id, **kwargs):
        post_link = link_tracker_id.th_post_link_ids

        values = {
            'campaign_name': link_tracker_id.campaign_id.name,
            'count_click': len(link_tracker_id.link_click_ids),
            'post_link': post_link,
            'page_name': 'post_link_info',
            'link_tracker': link_tracker_id,
        }

        return request.render("th_affiliate.th_post_link", values)

    @http.route('/my/post_link', type='http', auth="public", methods=['POST'], csrf=False, website=True)
    def create_post_link(self, **kwargs):
        link_tracker_id = int(kwargs.get('link_tracker_id', False))
        link = kwargs.get('link', False)
        link_tracker = request.env['link.tracker'].search([('id', '=', link_tracker_id)])
        post_link = request.env['th.post.link']
        if link and link_tracker.search([('th_closing_work', '=', 'pending')]):
            post_link = request.env['th.post.link'].create({
                'link_tracker_id': link_tracker_id,
                'name': link,
                'state': 'pending',
            })
        if post_link:
            message = {
                "status": 200,
                "msg": "Tạo thành công",
            }
        else:
            message = {
                "status": 400,
                "msg": "Tạo thất bại",
            }
        return Response(json.dumps(message))

    # Sản phẩm ngoài danh mục
    @http.route('/my/link_outside_view/', type='http', auth="public", methods=['GET'], website=True)
    def get_view_link(self, **kwargs):
        values = {
            'page_name': 'create_product_aff',
        }
        return request.render("th_affiliate.th_get_create_link_share_form", values)

    @http.route('/my/link_outside', type='http', auth="public", methods=['POST'], csrf=False, website=True,
                save_session=False)
    def create_link_outside(self, **kwargs):
        user_id = request.env.user.id
        url_product = kwargs['own_url']
        contact_affiliate = request.env['res.partner'].sudo().search([('user_ids.id', '=', user_id)], limit=1)
        link_tracker = request.env['link.tracker']
        domain = [
            ('th_aff_partner_id', '=', contact_affiliate.id),
            ('url', '=', url_product),
        ]
        link_exit = link_tracker.sudo().search(domain)
        if not link_exit:
            utm_source = request.env['utm.source'].sudo().search([('name', '=', contact_affiliate.th_affiliate_code)])
            if not utm_source and contact_affiliate:
                utm_source_id = utm_source.sudo().create({
                    'name': contact_affiliate.th_affiliate_code,
                }).id
            else:
                utm_source_id = utm_source.id

            request.env['link.tracker'].create({
                'th_aff_partner_id': contact_affiliate.id,
                'url': url_product,
                'source_id': utm_source_id,
            })

        return self.list_own_link_tracker()
