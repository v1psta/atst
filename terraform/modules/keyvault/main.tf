data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "keyvault" {
  name     = "${var.name}-${var.environment}-rg"
  location = var.region
}

resource "azurerm_key_vault" "keyvault" {
  name                = "${var.name}-${var.environment}-keyvault"
  location            = azurerm_resource_group.keyvault.location
  resource_group_name = azurerm_resource_group.keyvault.name
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "premium"

  tags = {
    environment = var.environment
    owner       = var.owner
  }
}
