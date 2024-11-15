/** @odoo-module **/
//import ajax from 'web.ajax';
import publicWidget from "@web/legacy/js/public/public_widget";
import { registry } from "@web/core/registry";

let id_tuples = undefined;

publicWidget.registry.WebsiteSale.include({
    async willStart() {
        await this._super.apply(this, arguments);

        const $parent = $(".js_product");
        const product_tmpl_id = $parent.find(".product_template_id").val();
        console.log("product_tmpl_id from server:", product_tmpl_id);

//        if (!sessionStorage.getItem("shipping_method_reloaded")) {
//            // Set a flag in sessionStorage to indicate the page has been reloaded
//            sessionStorage.setItem("shipping_method_reloaded", "true");
//            console.log(" inside ((((!sessionStorage.getItem(shipping_method_reloaded)")
//            // Reload the page
////            location.reload();
//        } else {
////            location.reload();
//             console.log("ELSEEEEEEEEEEEE")
//            // Auto-select the first available shipping method
//            this._autoSelectFirstShippingMethod();
//        }


        if (product_tmpl_id) {
            try {
                // Fetch product variant data using AJAX
                const response = await this._fetchProductVariantData(product_tmpl_id);

                // Log the response for debugging
                console.log("Response from server:", response);

                // Check for errors in the response
                if (response.error) {
                    console.error("Error from server:", response.message);
                    return;
                }

                // Check if the response contains the expected data
                if (response) {
                    id_tuples = response.result.data.value_to_show_tuple;
                    console.log("response>>>", response);
                    console.log("id_tuples>>>", id_tuples);

                    // Auto-select the first available variant
                    this._autoSelectFirstVariant($parent);
                } else {
                    console.error("Invalid data structure returned:", response);
                }
            } catch (error) {
                console.error("Failed to fetch product variant data:", error);
            }
        }
    },

    async _fetchProductVariantData(product_tmpl_id) {
        console.log("inside _fetchProductVariantData", product_tmpl_id);

        return $.ajax({
            type: "POST",
            dataType: "json",
            url: "/get_product_variant_data_website",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: { product_tmpl_id: product_tmpl_id },
            }),
        });
    },

    onChangeVariant(ev) {
        const instance = this;
        const $parent = $(ev.target).closest(".js_product");
        const $target = $(ev.target);

        if (!$parent.length || !id_tuples) {
            console.warn("No product context or id_tuples is undefined");
            return Promise.resolve();
        }

        if ($target.is("input[type=radio]") && $target.is(":checked")) {
            instance._hideVariants($target, $parent);
        } else {
            $target.find("input:checked").each(function () {
                instance._hideVariants($(this), $parent);
            });
        }

        return this._super.apply(this, arguments);
    },

    _hideVariants($target, $parent) {
        if (!id_tuples || !Array.isArray(id_tuples)) {
            console.warn("id_tuples is undefined or not an array");
            return;
        }

        const $variantContainer = $target.closest("ul").closest("li");
        const currentSelect = $variantContainer.attr("data-attribute_name");

        if (currentSelect === "SIZE") return;

        $parent
            .find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
            .each(function () {
                const $current = $(this);
                let firstShowed = null;
                let anyChecked = false;

                $current.find("input[type=radio]").each(function () {
                    const input = $(this);

                    const found = id_tuples.find((el) => {
                        const tupla = JSON.stringify(el);
                        const t1 = JSON.stringify([
                            parseInt($target.val()),
                            parseInt(input.val()),
                        ]);
                        const t2 = JSON.stringify([
                            parseInt(input.val()),
                            parseInt($target.val()),
                        ]);
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

                if (!anyChecked && firstShowed) {
                    firstShowed.prop("checked", true);
                }
            });
    },

    _autoSelectFirstVariant($parent) {
        // Find the first visible input for each attribute and select it
        $parent.find("li[data-attribute_display_type='radio']").each(function () {
            const $attribute = $(this);
            const $inputs = $attribute.find("input[type=radio]:visible");

            // Check if there are visible inputs and select the first one
            if ($inputs.length) {
                const $firstInput = $inputs.first();
                $firstInput.prop("checked", true).trigger("change");
            }
        });
    },

//     _autoSelectFirstShippingMethod() {
//        // Find the shipping methods within the delivery section
//        const $shippingMethods = $("#delivery_method .o_delivery_carrier_select input[type='radio']");
//
//        if ($shippingMethods.length > 0) {
//            // Select the first available shipping method
//            const $firstShippingMethod = $shippingMethods.first();
//
//            // Check if it's already selected; if not, select it and trigger change
//            if (!$firstShippingMethod.is(":checked")) {
//                $firstShippingMethod.prop("checked", true).trigger("change");
//                console.log("First shipping method auto-selected:", $firstShippingMethod.attr("id"));
//            }
//        } else {
//            console.warn("No shipping methods available to auto-select.");
//        }
//    }

    });




//import publicWidget from "@web/legacy/js/public/public_widget";
//import { registry } from '@web/core/registry';
//
//let id_tuples = undefined;
//
//publicWidget.registry.WebsiteSale.include({
//
//    async willStart() {
//        await this._super.apply(this, arguments);
//
//        let proms;
//        const $parent = $('.js_product');
//        const product_tmpl_id = parseInt($parent.find('.product_template_id').val());
//        if (product_tmpl_id) {
//               $.ajax({
//                    type: "POST",
//                    dataType: 'json', url:'/get_product_variant_data', 'call', {
//                'product_tmpl_id': product_tmpl_id,
//            }).then((data) => {
//                id_tuples = data;
//            });
//        }
//        await Promise.all([proms]);
//    },
//
//    onChangeVariant(ev) {
//        const instance = this;
//        const $parent = $(ev.target).closest('.js_product');
//        const $target = $(ev.target);
//
//        if (!$parent.length || !id_tuples) {
//            return Promise.resolve();
//        }
//
//        if ($target.is('input[type=radio]') && $target.is(':checked')) {
//            instance._hideVariants($target, $parent);
//        } else {
//            $target.find("input:checked")
//                .each(function () {
//                    instance._hideVariants($(this), $parent);
//                });
//        }
//
//        return this._super.apply(this, arguments);
//    },
//
//    _hideVariants($target, $parent) {
//        const $variantContainer = $target.closest('ul').closest('li');
//        const currentSelect = $variantContainer.attr('data-attribute_name');
//
//        if (currentSelect === 'SIZE') return;
//
//        $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
//            .each(function () {
//                const $current = $(this);
//                let firstShowed = null;
//                let anyChecked = false;
//
//                $current.find("input[type=radio]")
//                    .each(function () {
//                        const input = $(this);
//                        const found = id_tuples.value_to_show_tuple
//                            .find(function (el) {
//                                const tupla = JSON.stringify(el);
//                                const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
//                                const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);
//
//                                return tupla === t1 || tupla === t2;
//                            });
//                        if (!found) {
//                            input.parent().hide();
//                            input.prop("checked", false);
//                        } else {
//                            input.parent().show();
//                            if (firstShowed == null) {
//                                firstShowed = input;
//                            }
//                            if (!anyChecked) {
//                                anyChecked = input.is(":checked");
//                            }
//                        }
//                    });
//
//                if (!anyChecked && firstShowed) {
//                    firstShowed.prop("checked", true);
//                }
//            });
//    },
//});



 //odoo.define('hide_unavailable_variants', function (require) {



//    'use strict';
//    require("website_sale.website_sale")
//    var ajax = require('web.ajax');
//    var publicWidget = require('web.public.widget');
//    var id_tuples = undefined
//
//    publicWidget.registry.WebsiteSale.include({
//
//        willStart: async function () {
//            var proms;
//            const _super = this._super.apply(this, arguments);
//
//            var $parent = $('.js_product');
//            var product_tmpl_id = parseInt($parent.find('.product_template_id').val())
//            if (product_tmpl_id) {
//                proms = ajax.jsonRpc(this._getUri('/get_product_variant_data'), 'call', {
//                    'product_tmpl_id': product_tmpl_id,
//                }).then((data) => {
//                    id_tuples = data
//                });
//
//            }
//            return Promise.all([this._super(...arguments), proms]);
//        },
//
//        onChangeVariant: function (ev) {
//            const instance = this;
//
//            const $parent = $(ev.target).closest('.js_product');
//            const $target = $(ev.target)
//
//            if (!$parent.length || !id_tuples) {
//                return Promise.resolve();
//            }
//
//            if ($target.is('input[type=radio]') && $target.is(':checked')) {
//                instance._hideVariants($target, $parent)
//            } else {
//                $target.find("input:checked")
//                    .each(function (index) {
//                        instance._hideVariants($(this), $parent)
//                    });
//            }
//
//            this._super.apply(this, arguments);
//        },
//
//        _hideVariants($target, $parent) {
//
//            const $variantContainer = $target.closest('ul').closest('li');
//            const currentSelect = $variantContainer.attr('data-attribute_name')
//
//            if (currentSelect === 'SIZE') return;
//
//            $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
//                .each(function (index) {
//                    var $current = $(this)
//                    var firstShowed = null
//                    var anyChecked = false
//
//                    $current.find("input[type=radio]")
//                        .each(function (index) {
//                            var input = $(this);
//
//                            var found = id_tuples.value_to_show_tuple
//                                .find(function (el) {
//                                    const tupla = JSON.stringify(el);
//                                    const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
//                                    const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);
//
//                                    return tupla === t1 || tupla === t2
//                                });
//                            if (!found) {
//                                input.parent().hide()
//                                input.prop("checked", false);
//                            } else {
//                                input.parent().show();
//                                if (firstShowed == null)
//                                    firstShowed = input
//
//                                if (!anyChecked)
//                                    anyChecked = input.is(":checked")
//                            }
//                        });
//
//                    if (!anyChecked)
//                        firstShowed.prop("checked", true);
//                });
//
//        }
//    });
//});
