odoo.define('hide_unavailable_variants', function (require) {
    'use strict';

    const ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');
    let id_tuples = {};

    publicWidget.registry.WebsiteSale.include({

        /**
         * Override willStart to fetch product variant data before the widget starts.
         */
        async willStart() {
            await this._super.apply(this, arguments);

            const $parent = $('.js_product');
            const product_tmpl_id = parseInt($parent.find('.product_template_id').val());

            if (product_tmpl_id) {
                try {
                    const data = await ajax.jsonRpc('/get_product_variant_data', 'call', {
                        product_tmpl_id: product_tmpl_id,
                    });
                    id_tuples = data;
                } catch (error) {
                    console.error("Error fetching variant data:", error);
                }
            }
        },

        /**
         * Override onChangeVariant to dynamically hide unavailable options.
         */
        async onChangeVariant(ev) {
            await this._super.apply(this, arguments);

            const $parent = $(ev.target).closest('.js_product');
            const $target = $(ev.target);

            if (!$parent.length || !id_tuples) {
                return;
            }

            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                this._hideVariants($target, $parent);
            } else {
                $parent.find("input:checked").each((index, input) => {
                    this._hideVariants($(input), $parent);
                });
            }
        },

        /**
         * Custom method to hide unavailable product variants.
         */
        _hideVariants($target, $parent) {
            const $variantContainer = $target.closest('ul').closest('li');
            const currentSelect = $variantContainer.attr('data-attribute_name');

            if (currentSelect === 'SIZE') return;

            $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                .each(function () {
                    const $current = $(this);
                    let firstShowed = null;
                    let anyChecked = false;

                    $current.find("input[type=radio]").each(function () {
                        const input = $(this);

                        const found = id_tuples.value_to_show_tuple
                            .some(el => {
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
                            if (!firstShowed) firstShowed = input;
                            if (!anyChecked) anyChecked = input.is(":checked");
                        }
                    });

                    if (!anyChecked && firstShowed) {
                        firstShowed.prop("checked", true).trigger('change');
                    }
                });
        }
    });
});
