import '@testing-library/jest-dom'

// Polyfill for Request/Response
global.Request = class Request {
  constructor(input, init) {
    this.url = typeof input === 'string' ? input : input.url;
    this.method = init?.method || 'GET';
    this.body = init?.body || null;
    this.headers = new Map(Object.entries(init?.headers || {}));
  }
  
  async json() {
    return JSON.parse(this.body);
  }
  
  async text() {
    return this.body;
  }
};

global.Response = class Response {
  constructor(body, init) {
    this.body = body;
    this.status = init?.status || 200;
    this.headers = new Map(Object.entries(init?.headers || {}));
  }
  
  async json() {
    return typeof this.body === 'string' ? JSON.parse(this.body) : this.body;
  }
  
  async text() {
    return typeof this.body === 'string' ? this.body : JSON.stringify(this.body);
  }
};

global.Headers = class Headers {
  constructor(init) {
    this._headers = new Map(Object.entries(init || {}));
  }
  
  get(name) {
    return this._headers.get(name.toLowerCase());
  }
  
  set(name, value) {
    this._headers.set(name.toLowerCase(), value);
  }
};
