variable "aws_region" {
    type = string
    default = "eu-central-1"
}

variable "aws_env" {
    type = string
    default = "production"
}

variable "app_name" {
    type = string
    default = "ai_reviewer"
}

variable "instance_type" {
    type = string
    default = "t2.micro"
}

variable "public_key_path" {
    description = "Path to public SSH key"
    type = string
    default = "~/.ssh/id_rsa.pub"
}

variable "ami_id" {
    description = "AMI ID for EC2 instance"
    type = string
    default = "ami-0c7217cdde317cfec"
}