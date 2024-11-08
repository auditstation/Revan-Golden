odoo.define('hide_unavailable_variants', function (require) {
    'use strict';

    require("website_sale.website_sale");
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var id_tuples = undefined;

    publicWidget.registry.WebsiteSale.include({

        willStart: async function () {
            var proms;
            const _super = this._super.apply(this, arguments);

            var $parent = $('.js_product');
            var product_tmpl_id = parseInt($parent.find('.product_template_id').val());

            console.log('willStart - product_tmpl_id:', product_tmpl_id);  // Log the product_tmpl_id

            if (product_tmpl_id) {
                console.log('willStart - fetching variant data');  // Log before making the API call
                proms = ajax.jsonRpc(this._getUri('/get_product_variant_data'), 'call', {
                    'product_tmpl_id': product_tmpl_id,
                }).then((data) => {
                    id_tuples = data;
                    console.log('willStart - fetched data:', id_tuples);  // Log the fetched data
                });
            }

            return Promise.all([this._super(...arguments), proms]);
        },

        onChangeVariant: function (ev) {
            const instance = this;
            const $parent = $(ev.target).closest('.js_product');
            const $target = $(ev.target);

            console.log('onChangeVariant - $parent:', $parent.length, '$target:', $target);  // Log parent and target elements

            if (!$parent.length || !id_tuples) {
                console.log('onChangeVariant - no parent or no id_tuples');  // Log if no parent or id_tuples
                return Promise.resolve();
            }

            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                console.log('onChangeVariant - checking radio button');
                instance._hideVariants($target, $parent);
            } else {
                $target.find("input:checked")
                    .each(function (index) {
                        console.log('onChangeVariant - checking other input');
                        instance._hideVariants($(this), $parent);
                    });
            }

            this._super.apply(this, arguments);
        },

        _hideVariants($target, $parent) {
            const $variantContainer = $target.closest('ul').closest('li');
            const currentSelect = $variantContainer.attr('data-attribute_name');

            console.log('_hideVariants - currentSelect:', currentSelect);  // Log the current select

            if (currentSelect === 'SIZE') return;

            $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                .each(function (index) {
                    var $current = $(this);
                    var firstShowed = null;
                    var anyChecked = false;

                    console.log('_hideVariants - processing $current:', $current);  // Log the current element being processed

                    $current.find("input[type=radio]")
                        .each(function (index) {
                            var input = $(this);

                            var found = id_tuples.value_to_show_tuple
                                .find(function (el) {
                                    const tupla = JSON.stringify(el);
                                    const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                                    const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                                    console.log('_hideVariants - checking if variant pair is found:', t1, t2);  // Log the variant pair comparison

                                    return tupla === t1 || tupla === t2;
                                });

                            if (!found) {
                                console.log('_hideVariants - hiding variant:', input.val());  // Log the hidden variant
                                input.parent().hide();
                                input.prop("checked", false);
                            } else {
                                console.log('_hideVariants - showing variant:', input.val());  // Log the shown variant
                                input.parent().show();
                                if (firstShowed == null)
                                    firstShowed = input;

                                if (!anyChecked)
                                    anyChecked = input.is(":checked");
                            }
                        });

                    if (!anyChecked) {
                        console.log('_hideVariants - no variant checked, selecting first one');
                        firstShowed.prop("checked", true);
                    }
                });
        }
    });
});
