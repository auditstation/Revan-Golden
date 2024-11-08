odoo.define('hide_unavailable_variants', function (require) {
    'use strict';

    // Properly load required modules
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale'); // Ensure this is correctly required

    var id_tuples = undefined;

    // Extend WebsiteSale functionality
    publicWidget.registry.WebsiteSale.include({

        // Initialize and fetch product variant data
        willStart: async function () {
            var proms;
            const _super = this._super.apply(this, arguments);

            var $parent = $('.js_product');
            var product_tmpl_id = parseInt($parent.find('.product_template_id').val());
            if (product_tmpl_id) {
                proms = ajax.jsonRpc(this._getUri('/get_product_variant_data'), 'call', {
                    'product_tmpl_id': product_tmpl_id,
                }).then((data) => {
                    id_tuples = data;
                });
            }

            // Wait for both the super method and the promise to resolve
            return Promise.all([_super, proms]);
        },

        // Handle variant changes
        onChangeVariant: function (ev) {
            const instance = this;
            const $parent = $(ev.target).closest('.js_product');
            const $target = $(ev.target);

            // Skip if there's no parent element or no variant data
            if (!$parent.length || !id_tuples) {
                return Promise.resolve();
            }

            // Handle hiding/showing variants based on selection
            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                instance._hideVariants($target, $parent);
            } else {
                $target.find("input:checked").each(function () {
                    instance._hideVariants($(this), $parent);
                });
            }

            // Call the super method as well
            this._super.apply(this, arguments);
        },

        // Hide unavailable variants
        _hideVariants($target, $parent) {
            const $variantContainer = $target.closest('ul').closest('li');
            const currentSelect = $variantContainer.attr('data-attribute_name');

            // Skip 'SIZE' attribute
            if (currentSelect === 'SIZE') return;

            // Loop through other variants and hide unavailable ones
            $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                .each(function () {
                    var $current = $(this);
                    var firstShowed = null;
                    var anyChecked = false;

                    // Loop through the radio buttons for each variant
                    $current.find("input[type=radio]").each(function () {
                        var input = $(this);

                        // Find the matching variant from the tuples
                        var found = id_tuples.value_to_show_tuple
                            .find(function (el) {
                                const tupla = JSON.stringify(el);
                                const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                                const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                                return tupla === t1 || tupla === t2;
                            });

                        // If no match is found, hide the variant and uncheck it
                        if (!found) {
                            input.parent().hide();
                            input.prop("checked", false);
                        } else {
                            input.parent().show();
                            if (firstShowed == null) firstShowed = input;

                            if (!anyChecked) anyChecked = input.is(":checked");
                        }
                    });

                    // Ensure that at least one option is checked
                    if (!anyChecked) firstShowed.prop("checked", true);
                });
        }
    });
});
