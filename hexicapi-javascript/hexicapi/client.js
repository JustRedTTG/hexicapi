class TempCLI {
  constructor(id, socket) {
    this.id = id;
    this.socket = socket;
  }
}

class CalfManager {
  functions = {
    'connecting': undefined,
    'connection_warning': undefined,
    'connection_fail': undefined,
    'connection_success': undefined,
    'authenticating': undefined,
    'authentication_fail': undefined,
    'authentication_success': undefined,
    'handshake': undefined,
    'disconnect': undefined,
    'disconnect_soft': undefined,
    'heartbeat': undefined,
    'heartbeat_error': undefined,
    'registering': undefined,
    'registering_taken': undefined,
    'registering_complete': undefined,
    'version_warning': undefined,
    'version_info': undefined,
    'version_error': undefined
}
  constructor() {
  }
  async calf(type, reason) {
    let value = await this.get_msg(type, reason);
    if (value){ console.log(...value); }
  }
  async get_msg(type, reason) {
    if (!this.functions[type]) { return null; }
    return await this.functions[type](reason);
  }

  create_lambda_on_calf(enable_color, text, color) {
    if (enable_color) {
      return (reason) => {
        return [
          '%c'+text.replace('{reason}', reason),
          `color: ${color}`
        ];
      }
    } else {
      return (reason) => {
        return [
          text.replace('{reason}', reason)
        ];
      }
    }
  }

  basic_on_calf(enable_color) {
    this.functions['connecting'] = this.create_lambda_on_calf(enable_color, 'Connecting: {reason}', 'gold')
    this.functions['connection_warning'] = this.create_lambda_on_calf(enable_color, 'Connection error: {reason}', 'lightred')
    this.functions['connection_fail'] = this.create_lambda_on_calf(enable_color, 'Connection error: {reason}', 'lightred')
    this.functions['connection_success'] = this.create_lambda_on_calf(enable_color, 'Connection successful: {reason}', 'lightgreen')
    this.functions['authenticating'] = this.create_lambda_on_calf(enable_color, 'Authenticating: {reason}', 'gold')
    this.functions['authentication_fail'] = this.create_lambda_on_calf(enable_color, 'Authentication error: {reason}', 'lightred')
    this.functions['authentication_success'] = this.create_lambda_on_calf(enable_color, 'Authentication successful: {reason}', 'lightgreen')
    this.functions['handshake'] = this.create_lambda_on_calf(enable_color, 'Handshake: {reason}', 'lightgreen')
    this.functions['disconnect'] = this.create_lambda_on_calf(enable_color, 'Closing due to disconnect... {reason}', 'aqua')
    this.functions['disconnect_soft'] = this.create_lambda_on_calf(enable_color, 'Soft disconnect... {reason}', 'aqua')
    this.functions['heartbeat'] = this.create_lambda_on_calf(enable_color, 'Heartbeat: {reason}', 'aqua')
    this.functions['heartbeat_error'] = this.create_lambda_on_calf(enable_color, 'Heartbeat error: {reason}', 'lightred')
    this.functions['version_warning'] = this.create_lambda_on_calf(enable_color, 'Version warning: {reason}', 'peru')
    this.functions['version_info'] = this.create_lambda_on_calf(enable_color, 'Version information: {reason}', 'gray')
    this.functions['version_error'] = this.create_lambda_on_calf(enable_color, 'Version error: {reason}', 'lightred')
  }
}

class HexicAPIClient {
  auth_states = {
    'auth-declined': "Username or Password didn't get accepted",
    'auth-accepted': "Server accepted the details provided",
    'guest-declined': "Guest username didn't get accepted",
    'guest-declined-no-username': "Username declined because it was blank",
    'guest-accepted': "Server accepted the guest username provided",
    'auth-canceled': "Server cancelled authentication.",
  }
  constructor(ip, port, s, id, enc_private, enc_public, username, app, sm, te, td, cm) {
    this.ip = ip
    this.port = port
    this.socket = s
    this.id = id
    this.enc_private = enc_private
    this.enc_public = enc_public
    this.username = username
    this.app = app
    this.silent = false
    this.sm = sm
    this.te = te
    this.td = td
    this.cm = cm
  }
  async calf(type, msg) { await this.cm.calf(type, msg); }
  async send(message) {
    if (message instanceof Uint8Array) {
      await this.sm.send_all(this, message, false, this.enc_public)
    } else {
      await this.sm.send_all(this, this.te.encode(message), false, this.enc_public)
    }
    return true;
  }
  async auth(app, username, password, silent) {
    app = this.app || app;
    username = this.username || username;
    if (!silent){await this.calf('authenticating', "Called auth.")}
    let auth_result = 'auth-declined'
    try {
        await this.sm.send_all(this, this.te.encode(`auth:${username}:${password}:${app}`), false, this.enc_public);
        auth_result = this.td.decode(await this.sm.recv_all(this, this.sm.BUFFER_SIZE, false, this.enc_private));
    }
    catch(e) {await this.calf('disconnect', this.auth_states['auth-canceled']); throw(e);}

    if (auth_result === 'auth-declined' || auth_result === 'guest-declined') {this.calf('authentication_fail', this.auth_states[auth_result])}
    else if (!silent) {await this.calf('authentication_success', this.auth_states[auth_result])}
    if (auth_result === 'auth-accepted') {
      this.id = await this.heartbeat(true)
    }
  }
  async heartbeat(force_okay = false, silent = true) {
    let id = '';
    try {
      await this.sm.send_all(this, this.te.encode("clientGetID"), false, this.enc_public);
      id = this.td.decode(await this.sm.recv_all(this, this.sm.BUFFER_SIZE, false, this.enc_private));
    }
    catch(e) {id='';}
    if ((id === this.id) || force_okay) {
      if (!silent){await this.calf('heartbeat', "The server responded.")}
    }
    else {await this.calf('heartbeat_error', "The server didn't respond with the same id.")}
    return id;
  }
  async disconnect(softly = false, silent = true) {
    try {
      if (softly) {
        await this.sm.send_all(this, this.te.encode('bye_soft'), true);
      } else {
        await this.sm.send_all(this, this.te.encode('bye'), true);
      }
      await this.sm.recv_all(this)
    } catch (e) {}
    this.socket.close()
    if (softly && !silent) {
      await this.calf('disconnect_soft', "User called soft disconnect.")
    }
    else if (!softly) {
      await this.calf('disconnect', "User called disconnect.")
    }
  }
  async send(message) {
    let data;
    if (message instanceof String) {
      data = this.te.encode(message);
    } else if (message instanceof Uint8Array) { data = message; }
    try {
      await this.sm.send_all(this, data, false, this.enc_public);
    } catch(e) { return false; }
    return true;
  }
  async receive() {
    let data;
    try {
      data = await this.sm.recv_all(this, this.sm.BUFFER_SIZE, false, this.enc_private);
    } catch(e) { return; }
    try {
      data = this.td.decode(data);
    } catch (e) {}
    return data;
  }
}

class HexicAPI {
  constructor () {
    this.te = new TextEncoder();
    this.td = new TextDecoder();
    this.sm = new HexicAPImeesage();
    this.cm = new CalfManager();
  }
  HOST = "ws://localhost:81";
  BUFFER_SIZE = 2048;
  async calf(type, msg) { return await this.cm.calf(type, msg); }
  async run(app, username, password = '', autoauth = true, silent = false, connector = WebsocketConnector) {
    var s = new connector();
    if (!silent) {await this.calf('connecting', "The client was ran.");}
    try {
      await s.connect(this.HOST);
    }
    catch(e) {
      if (e instanceof AddressError){
        await this.calf('connection_fail', "Address malformed");
        return;
      }
      await this.calf('connection_fail', "Couldn't make a connection to the provided port and ip.");
      return;
    }
    
    if (!silent){await this.calf('connection_success', "Was able to connect to the server port and ip.");}
    await this.sm.send_all(s, this.te.encode("clientGetID"));
    var id_enc = this.td.decode(await this.sm.recv_all(s, this.BUFFER_SIZE, true));
    let version;
    let enc_public;
    let id;
    try {
      let data = id_enc.split('\r\n');
      id = data[0];
      version = data[1].split("'")[1];
      enc_public = data[2];
      if (version !== hexicapi_version){
        await this.calf('version_warning', `server: ${version} client: ${hexicapi_version}`);
      }
      else if (!silent) {
        await this.calf('version_info', version);
      }
    }
    catch(e){
      if (version !== hexicapi_version){
        await this.calf('connection_warning', "probably... banned or version error");
        await this.calf('version_error', `server: ${version} client: ${hexicapi_version}`);
      }
      else {
        await this.calf('connection_fail', "probably... banned or internal error");
      }
      return;
    }

    enc_public = await this.load_pem_public_key(enc_public
        .split('\n')
        .slice(1, -2)
        .join('')
        .trim()
    );
    let public_key;
    let enc_private;
    [enc_private, public_key] = await this.generate_key();

    await this.sm.send_all(new TempCLI(id, s), await this.publicKeyToPem(public_key), true);
    await this.sm.recv_all(new TempCLI(id, s), this.sm.PACKET_SIZE, false, enc_private);

    if (!silent){await this.calf('handshake', "Encryption handshake.");}
    
    let cli = new HexicAPIClient(s.getsockname(), 0, s, id, enc_private, enc_public, username, app, this.sm, this.te, this.td, this.cm);
    
    if (autoauth) {
      if (!silent){await this.calf('authenticating', "Autoauth was enabled.");}
      await cli.auth(0, 0, password, silent)
    }
    cli.silent = silent
    return cli
  }
  async load_pem_public_key(publicKey) {
    const binaryString = window.atob(publicKey);
    const publicKeyBuffer = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      publicKeyBuffer[i] = binaryString.charCodeAt(i);
    }

    const cryptoKey = await crypto.subtle.importKey(
      'spki',
      publicKeyBuffer.buffer,
      {
        name: 'RSA-OAEP',
        hash: 'SHA-256'
      },
      true,
      ['encrypt']
    );
    return cryptoKey;
  }

  async generate_key() {
    let keyPair = await crypto.subtle.generateKey({
      name: "RSA-OAEP",
      modulusLength: 2048,
      publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
      hash: { name: "SHA-256" }
    }, true, ["encrypt", "decrypt"]);

    return [keyPair.privateKey, keyPair.publicKey];
  }

  async publicKeyToPem(publicKey) {
    const exportedKey = await crypto.subtle.exportKey("spki", publicKey);
    const exportedKeyBytes = new Uint8Array(exportedKey);
    const base64ExportedKey = btoa(String.fromCharCode.apply(null, exportedKeyBytes));

    let pemExportedKey = "";
    for (let i = 0; i < base64ExportedKey.length; i += 64) {
      pemExportedKey += base64ExportedKey.slice(i, i + 64) + "\n";
    }
    pemExportedKey =
      "-----BEGIN PUBLIC KEY-----\n" + pemExportedKey + "-----END PUBLIC KEY-----\n";

    const pemExportedKeyBytes = new TextEncoder().encode(pemExportedKey);
    return new Uint8Array(pemExportedKeyBytes);
  }
}