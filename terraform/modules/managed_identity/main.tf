resource "azurerm_resource_group" "identity" {
  name     = "${var.name}-${var.environment}-${var.identity}"
  location = var.region
}

resource "azurerm_user_assigned_identity" "identity" {
  resource_group_name = azurerm_resource_group.identity.name
  location            = azurerm_resource_group.identity.location

  name = "${var.name}-${var.environment}-${var.identity}"
}