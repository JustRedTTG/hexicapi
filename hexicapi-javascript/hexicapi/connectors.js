function AddressError() {}
AddressError.prototype = new Error();

class Connector {
  sockname = 'client';
  s = undefined;
  constructor() {
    this.buffer = new Uint8Array(new ArrayBuffer())
  }
  connect(address) {}
  send(bytes) {}
  recv(buffer) {}
  close() {}
  getsockname() { return this.sockname; }
}

class WebsocketConnector extends Connector {
  constructor() {
    super();
  }
  async connect(address) {
    this.s = new WebSocket(address);
    this.s.addEventListener('error', (error) => {
      throw("couldn't connect");
    });
 
    this.s.addEventListener("message", async (event) => {
      let newa = new Uint8Array(await event.data.arrayBuffer());
      let temp = new Uint8Array(this.buffer.length + newa.length);
      temp.set(this.buffer, 0);
      temp.set(newa, this.buffer.length);
      this.buffer = temp;
    });
    return new Promise(resolve => {
      this.s.addEventListener('open', () => {
        resolve(this);
      });
    });
  }
  async send(bytes) { return await this.s.send(bytes); }
  //async recv(buffer) { return this.buffer.shift().arrayBuffer(); }
  async recv(amount) {
    while (this.buffer.length < 1) {
      await new Promise(resolve => setTimeout(resolve, 10)); // wait for messages to arrive
    }
    // console.log("AND IT GOES THROUGH THE ROOF", this.buffer.length)
    let res = this.buffer.slice(0, amount)
    let temp = new Uint8Array(this.buffer.length - res.length);
    temp.set(this.buffer.subarray(amount), 0);
    this.buffer = temp;
    return res;
  }
}