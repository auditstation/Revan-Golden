import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";

patch(ProductsWidget.prototype, {
    async onProducttestttt(product) {
        const info = await this.pos.getProductInfo(product, 1);
        this.popup.add(ProductInfoPopup, { info: info, product: product });
    }
});