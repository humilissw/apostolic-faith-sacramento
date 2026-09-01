// Learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";

// jsdom does not implement window.matchMedia (used by hooks/use-mobile.ts)
if (typeof window !== "undefined" && !window.matchMedia) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: (query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }),
  });
}

// jsdom does not implement the Fetch API Response class used by tests that mock global.fetch
if (typeof Response === "undefined") {
  class TestResponse {
    constructor(body = null, options = {}) {
      this.body = body;
      this.status = options.status ?? 200;
      this.statusText = options.statusText ?? "";
      this.headers = new Map(Object.entries(options.headers ?? {}));
    }

    get ok() {
      return this.status >= 200 && this.status < 300;
    }

    async json() {
      return JSON.parse(this.body);
    }

    async text() {
      return this.body ?? "";
    }
  }

  global.Response = TestResponse;
}
