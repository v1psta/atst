module "sql" {
  source      = "../../modules/postgres"
  name        = var.name
  owner       = var.owner
  environment = var.environment
  region      = var.region
  subnet_id   = module.vpc.subnets # FIXME - Should be a map of subnets and specify private
}
