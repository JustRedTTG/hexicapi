class HexicAPImeesage {
  public_key = '';
  PACKET_SIZE = 1048
  constructor() {
    this.te = new TextEncoder();
    this.td = new TextDecoder();
  }

  connection_init(client, enc) {
    let the_socket;
    let client_id;
    if (client instanceof WebsocketConnector) {
      the_socket = client;
      client_id = client.getsockname();
    } else {
      the_socket = client.socket;
      client_id = client.id;
    }
    let menc = enc || this.enc_public;
    return [the_socket, client_id, menc];
  }
  async send_all(client, data, skip=false, enc) {
    let [the_socket, client_id, menc] = this.connection_init(client, enc);
    if (menc) {
      data = new Uint8Array(await crypto.subtle.encrypt(
        {name: "RSA-OAEP"},
        menc,
        data
      ));
    }
    let length = new Uint8Array(16);
    let lengthStr = this.te.encode(data.length.toString());
    let lengthOffset = 16 - lengthStr.length;
    length.fill(48, 0, lengthOffset)
    length.set(lengthStr, lengthOffset)

    the_socket.send(length);
    the_socket.send(data);
  }
  async recv_all(client, packet_size=1024, skip=false, enc) {
    let [the_socket, client_id, menc] = this.connection_init(client, enc);

    let size = parseInt(this.td.decode(await the_socket.recv(16)));
    let data = await the_socket.recv(size);
    if (menc && !skip) {
      data = await crypto.subtle.decrypt(
          {name: "RSA-OAEP"},
          menc,
          data
      )
    }

    return data
  }
}