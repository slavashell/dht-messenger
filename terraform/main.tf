terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token     = "${var.yc_token}"
  cloud_id  = "${var.yc_cloud}"
  folder_id = "${var.yc_folder}"
  zone      = "ru-central1-a"
}

data "yandex_compute_image" "container-optimized-image" {
  family = "container-optimized-image"
}

resource "yandex_compute_instance" "dht-messenger" {
  count       = 5
  name        = "dht-messenger-${count.index}"
  platform_id = "standard-v2"

  resources {
    cores         = 2
    memory        = 1
    core_fraction = 5
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.container-optimized-image.id
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
  }

  metadata = {
    user_data = templatefile(
      "${path.module}/files/user-data.tpl",
      {
        user = var.user
        ssh-key = "${local.public_ssh_key}"
      }
    )
    docker-container-declaration = file("${path.module}/declaration.yaml")
  }
}

resource "yandex_vpc_network" "network" {
  name = "network"
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "public-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}
