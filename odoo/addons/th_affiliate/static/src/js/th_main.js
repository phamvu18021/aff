/** @odoo-module **/

import rpc from 'web.rpc';
import { onWillStart } from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import {ListController} from "@web/views/list/list_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

// const list_model = ['th.opportunity.ctv']
patch(ListController.prototype, 'th_affiliate.ListController', {
    setup() {
        this._super.apply(this, arguments);
        this.user = useService("user");
        onWillStart(async () => {
            this.isModel = await this.check_model_help()
            // this.isSampleImport = await this.check_sample_import()
        });
    },
    async check_model_help() {
        // list_model.includes(this.props.resModel) &&
        if (await this.user.hasGroup("th_affiliate.group_aff_officer")) return true
        return false
    },

    async onClickSynchronizeData() {
        let th_company = this.props.context.allowed_company_ids
        const confirmed = await this.dialogService.add(ConfirmationDialog, {
            title: "Xác nhận đồng bộ",
            body: "Bạn có chắc chắn muốn đồng bộ hoá dữ liệu?",
            confirm: async () => {
                await rpc.query({
                    model: 'th.opportunity.ctv',
                    method: 'th_action_synchronize_data',
                    args: [[], null, th_company],
                });
                return this.actionService.doAction({
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                });
            },
            cancel: () => {},
        });
    },

    async onClickSyncDataWarehouse() {
        const confirmed = await this.dialogService.add(ConfirmationDialog, {
            title: "Xác nhận đồng bộ",
            body: "Bạn có chắc chắn muốn đồng bộ dữ liệu kho?",
            confirm: async () => {
                await rpc.query({
                    model: 'th.warehouse',
                    method: 'th_sync_warehouse',
                    args: [[]],
                });
                return this.actionService.doAction({
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                });
            },
            cancel: () => {
            },
        });
    },

    async onClickSyncDataOrder() {
        const confirmed = await this.dialogService.add(ConfirmationDialog, {
            title: "Xác nhận đồng bộ",
            body: "Bạn có chắc chắn muốn đồng bộ dữ liệu đơn hàng?",
            confirm: async () => {
                await rpc.query({
                    model: 'th.aff.order',
                    method: 'th_action_sync_orders',
                    args: [[]],
                });
                return this.actionService.doAction({
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                });
            },
            cancel: () => {
            },
        });
    },

    // async check_sample_import() {
    //     var result = await rpc.query({
    //         context: this.props.context,
    //         model: 'report.th_affiliate.sample_import_xlsx',
    //         method: 'action_report_excel',
    //          args: [[]],
    //         }).then((id)=>{
    //             return this.actionService.doAction({
    //                 type: 'ir.actions.act_url',
    //                 url: `/report/xlsx/th_affiliate.sample_import_xlsx/${id}`,
    //                 target: 'new',
    //             });
    //         })
    // },

});
