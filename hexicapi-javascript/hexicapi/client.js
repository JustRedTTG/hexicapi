class HexicAPIClient {
  constructor() {
    
  }
}

class HexicAPI {
  constructor () {
    this.te = new TextEncoder();
    this.td = new TextDecoder();
    this.sm = new HexicAPImeesage();
  }
  HOST = "ws://localhost:81";
  BUFFER_SIZE = 2048;
  calf(type, msg) {
    console.log(type, msg);
  }
  async run(app, username, password = '', autoauth = true, silent = false, connector = WebsocketConnector) {
    var s = new connector();
    if (!silent) {this.calf('connecting', "The client was ran.");}
    try {
      await s.connect(this.HOST);
    }
    catch(e) {
      if (e instanceof AddressError){
        this.calf('connection_fail', "Address malformed");
        return;
      }
      this.calf('connection_fail', "Couldn't make a connection to the provided port and ip.");
      console.log(e);
      return;
    }
    
    if (!silent){this.calf('connection_success', "Was able to connect to the server port and ip.");}
    this.sm.send_all(s, this.te.encode("clientGetID"));
    var id_enc = this.td.decode(await this.sm.recv_all(s, this.BUFFER_SIZE, true));
    console.log("clientGetId", id_enc);
    try {
      data = id_enc.split('\r\n');
      id = data[0];
      var version = data[1].split("'")[1];
      enc_public = data[2];
      if (version != hexicapi_version){
        this.calf('version_warning', `server: ${version} client: ${hexicapi_version}`);
      }
      else if (!silent) {
        this.calf('version_info', version);
      }
    }
    catch(e){
      if (version != hexicapi_version){
        this.calf('connection_warning', "probably... banned or version error");
        this.calf('version_error', `server: ${version} client: ${hexicapi_version}`);
      }
      else {
        this.calf('connection_fail', "probably... banned or internal error");
      }
      return;
    }
    
    enc_public = enc_public.encode('utf-8');
    enc_public = serialization.load_pem_public_key(
      enc_public
    );
    enc_private, public_key = generate_keys();
    send_all(CLI(id, s), public_key, true);
    recv_all(CLI(id, s), false, enc_private);
    if (!silent){this.calf('handshake', "Encryption handshake.");}
    
    cli = HexicAPIClient(s.getsockname(), s, id, enc_private, enc_public, username, app);
    
    if (autoauth) {
      if (!silent){this.calf('authenticating', "Autoauth was enabled.");}
      cli.auth(password = password, silent = silent)
    }
    cli.silent = silent
    return cli
  }
}