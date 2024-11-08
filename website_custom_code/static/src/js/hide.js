odoo.define('hide_unavailable_variants', function (require) {
    'use strict';

    const { Component } = require('web.core');
    const ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');

    let id_tuples = undefined;

    publicWidget.registry.WebsiteSale.include({

        willStart: async function () {
            const _super = this._super.apply(this, arguments);
            let proms;
            const $parent = $('.js_product');
            const product_tmpl_id = parseInt($parent.find('.product_template_id').val());

            if (product_tmpl_id) {
                proms = ajax.jsonRpc(this._getUri('/get_product_variant_data'), 'call', {
                    'product_tmpl_id': product_tmpl_id,
                }).then((data) => {
                    id_tuples = data;
                });
            }

            return Promise.all([_super, proms]);
        },

        onChangeVariant: function (ev) {
            const instance = this;
            const $parent = $(ev.target).closest('.js_product');
            const $target = $(ev.target);

            if (!$parent.length || !id_tuples) {
                return Promise.resolve();
            }

            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                instance._hideVariants($target, $parent);
            } else {
                $target.find("input:checked").each(function () {
                    instance._hideVariants($(this), $parent);
                });
            }

            return this._super.apply(this, arguments);
        },

        _hideVariants($target, $parent) {
            const $variantContainer = $target.closest('ul').closest('li');
            const currentSelect = $variantContainer.attr('data-attribute_name');

            if (currentSelect === 'SIZE') return;

            $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`).each(function () {
                const $current = $(this);
                let firstShowed = null;
                let anyChecked = false;

                $current.find("input[type=radio]").each(function () {
                    const input = $(this);

                    const found = id_tuples.value_to_show_tuple.find(function (el) {
                        const tupla = JSON.stringify(el);
                        const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                        const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                        return tupla === t1 || tupla === t2;
                    });

                    if (!found) {
                        input.parent().hide();
                        input.prop("checked", false);
                    } else {
                        input.parent().show();
                        if (firstShowed == null) firstShowed = input;
                        if (!anyChecked) anyChecked = input.is(":checked");
                    }
                });

                if (!anyChecked) firstShowed.prop("checked", true);
            });
        }
    });
});