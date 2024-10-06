from server.overrides import ModelTextChoices


class DigitalOrderStatusChoices(ModelTextChoices):
    PLACED = "001", "Order Placed"
    PROCESSING = "002", "Order Processing"
    COMPLETED = "003", "Order Completed"
    CANCEL = "004", "Cancelled"


class PaymentMethods(ModelTextChoices):
    CARD = "card", "Credit Card/Detail Card"
    KLARNA = "klarna", "Klarna"
    PAYPAL = "paypal", "PayPal"
