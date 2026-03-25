terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.92"
        }
    }
    required_version = ">= 1.2"
}

provider "aws" {
    region = var.aws_region
    default_tags {
        tags = {
            Environment = var.aws_env
            projet = var.app_name
            ManagedBy = "Terraform"
            OwnedBy = "Khalil"
        }
    }
}
