resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "main"
  }
  enable_dns_hostnames = true
  enable_dns_support = true
}
data "aws_availability_zones" "available" {
  state = "available"
}
locals {
  azs = slice(data.aws_availability_zones.available.names , 0 ,2)
  public_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  private_cidrs = ["10.0.101.0/24","10.0.102.0/24"]
}

resource "aws_subnet" "public" {
  availability_zone = local.azs[count.index]
  count = length(local.azs)
  vpc_id = aws_vpc.main.id
  cidr_block = local.public_cidrs[count.index]
  map_public_ip_on_launch = true
  tags= {
    Name = "public-subnet-${count.index}"
    "kubernetes.io/role/elb"              = "1"
    "kubernetes.io/cluster/aegis-cluster-01" = "shared"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags={
    Name = "main-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags={
    Name = "public-rt"
  }
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  count = length(local.azs)
  subnet_id = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(local.azs)
  subnet_id = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_subnet" "private" {
  map_public_ip_on_launch = false
  vpc_id = aws_vpc.main.id
  count = length(local.azs)
  availability_zone = local.azs[count.index]
  cidr_block = local.private_cidrs[count.index]
  tags = {
    Name = "private-subnet-${count.index}"
    "kubernetes.io/role/internal-elb"              = "1"
    "kubernetes.io/cluster/aegis-cluster-01" = "shared"
}
}


resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags={
    Name = "private-rt"
  }
}