locals {
  public_ssh_key = "${file("~/.ssh/id_rsa.pub")}"
}
