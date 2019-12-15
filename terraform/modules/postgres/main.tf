resource "azurerm_resource_group" "sql" {
  name     = "${var.name}-${var.environment}-postgres"
  location = var.region
}

resource "azurerm_postgresql_server" "sql" {
  name                = "${var.name}-${var.environment}-sql"
  location            = azurerm_resource_group.sql.location
  resource_group_name = azurerm_resource_group.sql.name

  sku {
    name     = var.sku_name
    capacity = var.sku_capacity
    tier     = var.sku_tier
    family   = var.sku_family
  }

  storage_profile {
    storage_mb            = var.storage_mb
    backup_retention_days = var.storage_backup_retention_days
    geo_redundant_backup  = var.storage_geo_redundant_backup
    auto_grow             = var.stroage_auto_grow
  }

  administrator_login          = "sqladmindude"
  administrator_login_password = "eI0l7yswwtuhHpwzoVjwRKdAcuGNsg"
  version                      = "11"
  ssl_enforcement              = "Enabled"
}

resource "azurerm_postgresql_virtual_network_rule" "sql" {
  name                                 = "postgresql-vnet-rule"
  resource_group_name                  = azurerm_resource_group.sql.name
  server_name                          = azurerm_postgresql_server.sql.name
  subnet_id                            = var.subnet_id
  ignore_missing_vnet_service_endpoint = true
}