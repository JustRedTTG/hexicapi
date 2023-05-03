class HexicAPImeesage {
  send_all(client, data, skip=false, enc=undefined) {
    client.send(data);
  }
  async recv_all(client, packet_size=1024, skip=false, enc=undefined) {
    return await client.recv(packet_size);
  }
}