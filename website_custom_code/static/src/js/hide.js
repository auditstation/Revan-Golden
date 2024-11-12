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
            const instance = this;

            const $parent = $(ev.target).closest('.js_product');
            const $target = $(ev.target)

            if (!$parent.length || !id_tuples) {
                return Promise.resolve();
            }

            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                instance._hideVariants($target, $parent)
            } else {
                $target.find("input:checked")
                    .each(function (index) {
                        instance._hideVariants($(this), $parent)
                    });
            }

            this._super.apply(this, arguments);
        },

        _hideVariants($target, $parent) {

            const $variantContainer = $target.closest('ul').closest('li');
            const currentSelect = $variantContainer.attr('data-attribute_name')

            if (currentSelect === 'SIZE') return;

            $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                .each(function (index) {
                    var $current = $(this)
                    var firstShowed = null
                    var anyChecked = false

                    $current.find("input[type=radio]")
                        .each(function (index) {
                            var input = $(this);

                            var found = id_tuples.value_to_show_tuple
                                .find(function (el) {
                                    const tupla = JSON.stringify(el);
                                    const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                                    const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                                    return tupla === t1 || tupla === t2
                                });
                            if (!found) {
                                input.parent().hide()
                                input.prop("checked", false);
                            } else {
                                input.parent().show();
                                if (firstShowed == null)
                                    firstShowed = input

                                if (!anyChecked)
                                    anyChecked = input.is(":checked")
                            }
                        });

                    if (!anyChecked)
                        firstShowed.prop("checked", true);
                });

        }
    });
});
