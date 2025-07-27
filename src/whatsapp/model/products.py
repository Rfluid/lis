from pydantic import BaseModel, Field


class ProductItem(BaseModel):
    product_retailer_id: str = Field(description="Retailer ID of the product.")


class OrderData(BaseModel):
    catalog_id: str = Field(
        description="Catalog ID from which the product was selected."
    )
    product_items: list[ProductItem] = Field(
        description="List of products in the order."
    )
