odoo.define('hide_unavailable_variants', function (require) {
    'use strict';
    require("website_sale.website_sale")
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var id_tuples = undefined

    publicWidget.registry.WebsiteSale.include({

        willStart: async function () {
            var proms;
            const _super = this._super.apply(this, arguments);

            var $parent = $('.js_product');
            var product_tmpl_id = parseInt($parent.find('.product_template_id').val())
            if (product_tmpl_id) {
                proms = ajax.jsonRpc(this._getUri('/get_product_variant_data'), 'call', {
                    'product_tmpl_id': product_tmpl_id,
                }).then((data) => {
                    id_tuples = data
                });

            }
            return Promise.all([this._super(...arguments), proms]);
        },

        onChangeVariant: function (ev) {
            // console.log(`im here: onChangeVariant ${JSON.stringify(ev)}`)

            const $parent = $(ev.target).closest('.js_product');
            const $target = $(ev.target)
            var $variantContainer;

            if (!$parent.length) {
                return Promise.resolve();
            }
            const combination = this.getSelectedVariantValues($parent);
            console.log(`${combination} || ${$target.attr('data-attribute_name')}`)


            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                $parent.find("input[type=radio]")
                    .each(function (index) {
                        $(this).parent().show()
                    });

                $variantContainer = $target.closest('ul').closest('li');
                const currentSelect = $variantContainer.attr('data-attribute_name')

                $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                    .each(function (index) {
                        var $current = $(this)

                        $current.find("input[type=radio]")
                            .each(function (index) {
                                var input = $(this);

                                if (!id_tuples.value_to_show_tuple
                                    .find(function (el) {
                                        const tupla = JSON.stringify(el);
                                        const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                                        const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                                        return tupla === t1 || tupla === t2
                                    })) {

                                    input.parent().hide()
                                }
                            });
                    });
            } else {
                $target.find("input:checked")
                    .each(function (index) {
                        var $target = $(this)
                        $variantContainer = $target.closest('ul').closest('li');

                        const currentSelect = $variantContainer.attr('data-attribute_name')

                        $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                            .each(function (index) {
                                var $current = $(this)

                                $current.find("input[type=radio]")
                                    .each(function (index) {
                                        var input = $(this);

                                        if (!id_tuples.value_to_show_tuple
                                            .find(function (el) {
                                                const tupla = JSON.stringify(el);
                                                const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                                                const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                                                return tupla === t1 || tupla === t2
                                            })) {

                                            input.parent().hide()
                                        }
                                    });
                            });
                    });
            }

            this._super.apply(this, arguments);
        },

        hideVariants($target, $parent) {

        }
    });
});