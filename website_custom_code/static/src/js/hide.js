odoo.define('hide_unavailable_variants', function (require) {
    'use strict';

    // Load required modules
    require(["website_sale.website_sale", "web.ajax", "web.public.widget"], function (WebsiteSale, ajax, publicWidget) {
        var id_tuples = undefined;

        publicWidget.registry.WebsiteSale.include({

            // Modify the willStart method to load product variant data
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
                return Promise.all([this._super(...arguments), proms]);
            },

            // Modify the onChangeVariant method to hide unavailable variants
            onChangeVariant: function (ev) {
                const instance = this;
                const $parent = $(ev.target).closest('.js_product');
                const $target = $(ev.target);

                // If no parent element or id_tuples is undefined, skip the logic
                if (!$parent.length || !id_tuples) {
                    return Promise.resolve();
                }

                // Handle the variant change by hiding the unavailable variants
                if ($target.is('input[type=radio]') && $target.is(':checked')) {
                    instance._hideVariants($target, $parent);
                } else {
                    $target.find("input:checked")
                        .each(function (index) {
                            instance._hideVariants($(this), $parent);
                        });
                }

                this._super.apply(this, arguments);
            },

            // Custom method to hide unavailable variants
            _hideVariants($target, $parent) {
                const $variantContainer = $target.closest('ul').closest('li');
                const currentSelect = $variantContainer.attr('data-attribute_name');

                // Skip if the variant is related to 'SIZE'
                if (currentSelect === 'SIZE') return;

                // Loop through other variants and hide the ones that are not available
                $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
                    .each(function (index) {
                        var $current = $(this);
                        var firstShowed = null;
                        var anyChecked = false;

                        // Loop through the radio buttons for each variant
                        $current.find("input[type=radio]")
                            .each(function (index) {
                                var input = $(this);

                                // Find the tuple that matches the selected variant
                                var found = id_tuples.value_to_show_tuple
                                    .find(function (el) {
                                        const tupla = JSON.stringify(el);
                                        const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                                        const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);

                                        return tupla === t1 || tupla === t2;
                                    });

                                // If a matching variant is not found, hide it and uncheck
                                if (!found) {
                                    input.parent().hide();
                                    input.prop("checked", false);
                                } else {
                                    input.parent().show();
                                    if (firstShowed == null) firstShowed = input;

                                    if (!anyChecked) anyChecked = input.is(":checked");
                                }
                            });

                        // Ensure at least one variant is selected if none are checked
                        if (!anyChecked) firstShowed.prop("checked", true);
                    });
            }
        });
    });
});
