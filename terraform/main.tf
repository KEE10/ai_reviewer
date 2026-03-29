resource "aws_key_pair" "app_key_pair" {
    key_name = "${var.app_name}-${var.aws_env}-key"
    public_key = file(var.public_key_path)
}

resource "aws_security_group" "app_sg" {
    name = "${var.app_name}-${var.aws_env}-sg"
    vpc_id = data.aws_vpc.default_vpc.id

    ingress {
        description = "SSH access"
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"] # TODO: change later to GH IP range
    }

    ingress {
        description = "Https"
        from_port = 443
        to_port = 443
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"] # TODO: change later to GH IP range
    }

    egress {
        description = "DB outbound"
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"] # TODO: change later to supabase IP range
    }

    egress {
        description = "Https outbound"
        from_port = 0
        to_port = 65535
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_instance" "app" {
    ami = var.ami_id
    instance_type = var.instance_type
    key_name = aws_key_pair.app_key_pair.key_name
    vpc_security_group_ids = [aws_security_group.app_sg.id]

    associate_public_ip_address = true
    user_data     = <<-EOF
        #!/bin/bash
        yum update -y
        yum install -y docker
        systemctl enable docker
        systemctl start docker
        usermod -aG docker ec2-user
        mkdir -p /app
        chown ec2-user:ec2-user /app
        chmod 755 /app

        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    EOF
}

resource "aws_eip" "app_eip" {
    domain = "vpc"
    instance = aws_instance.app.id
    depends_on = [aws_instance.app]
}
