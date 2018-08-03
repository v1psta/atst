// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles

// eslint-disable-next-line no-global-assign
parcelRequire = (function (modules, cache, entry, globalName) {
  // Save the require from previous bundle to this closure if any
  var previousRequire = typeof parcelRequire === 'function' && parcelRequire;
  var nodeRequire = typeof require === 'function' && require;

  function newRequire(name, jumped) {
    if (!cache[name]) {
      if (!modules[name]) {
        // if we cannot find the module within our internal map or
        // cache jump to the current global require ie. the last bundle
        // that was added to the page.
        var currentRequire = typeof parcelRequire === 'function' && parcelRequire;
        if (!jumped && currentRequire) {
          return currentRequire(name, true);
        }

        // If there are other bundles on this page the require from the
        // previous one is saved to 'previousRequire'. Repeat this as
        // many times as there are bundles until the module is found or
        // we exhaust the require chain.
        if (previousRequire) {
          return previousRequire(name, true);
        }

        // Try the node require function if it exists.
        if (nodeRequire && typeof name === 'string') {
          return nodeRequire(name);
        }

        var err = new Error('Cannot find module \'' + name + '\'');
        err.code = 'MODULE_NOT_FOUND';
        throw err;
      }

      localRequire.resolve = resolve;

      var module = cache[name] = new newRequire.Module(name);

      modules[name][0].call(module.exports, localRequire, module, module.exports, this);
    }

    return cache[name].exports;

    function localRequire(x){
      return newRequire(localRequire.resolve(x));
    }

    function resolve(x){
      return modules[name][1][x] || x;
    }
  }

  function Module(moduleName) {
    this.id = moduleName;
    this.bundle = newRequire;
    this.exports = {};
  }

  newRequire.isParcelRequire = true;
  newRequire.Module = Module;
  newRequire.modules = modules;
  newRequire.cache = cache;
  newRequire.parent = previousRequire;
  newRequire.register = function (id, exports) {
    modules[id] = [function (require, module) {
      module.exports = exports;
    }, {}];
  };

  for (var i = 0; i < entry.length; i++) {
    newRequire(entry[i]);
  }

  if (entry.length) {
    // Expose entry point to Node, AMD or browser globals
    // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
    var mainExports = newRequire(entry[entry.length - 1]);

    // CommonJS
    if (typeof exports === "object" && typeof module !== "undefined") {
      module.exports = mainExports;

    // RequireJS
    } else if (typeof define === "function" && define.amd) {
     define(function () {
       return mainExports;
     });

    // <script>
    } else if (globalName) {
      this[globalName] = mainExports;
    }
  }

  // Override the current require with this new one
  return newRequire;
})({"../node_modules/parcel/src/builtins/bundle-url.js":[function(require,module,exports) {
var bundleURL = null;
function getBundleURLCached() {
  if (!bundleURL) {
    bundleURL = getBundleURL();
  }

  return bundleURL;
}

function getBundleURL() {
  // Attempt to find the URL of the current script and use that as the base URL
  try {
    throw new Error();
  } catch (err) {
    var matches = ('' + err.stack).match(/(https?|file|ftp):\/\/[^)\n]+/g);
    if (matches) {
      return getBaseURL(matches[0]);
    }
  }

  return '/';
}

function getBaseURL(url) {
  return ('' + url).replace(/^((?:https?|file|ftp):\/\/.+)\/[^/]+$/, '$1') + '/';
}

exports.getBundleURL = getBundleURLCached;
exports.getBaseURL = getBaseURL;
},{}],"../node_modules/parcel/src/builtins/css-loader.js":[function(require,module,exports) {
var bundle = require('./bundle-url');

function updateLink(link) {
  var newLink = link.cloneNode();
  newLink.onload = function () {
    link.remove();
  };
  newLink.href = link.href.split('?')[0] + '?' + Date.now();
  link.parentNode.insertBefore(newLink, link.nextSibling);
}

var cssTimeout = null;
function reloadCSS() {
  if (cssTimeout) {
    return;
  }

  cssTimeout = setTimeout(function () {
    var links = document.querySelectorAll('link[rel="stylesheet"]');
    for (var i = 0; i < links.length; i++) {
      if (bundle.getBaseURL(links[i].href) === bundle.getBundleURL()) {
        updateLink(links[i]);
      }
    }

    cssTimeout = null;
  }, 50);
}

module.exports = reloadCSS;
},{"./bundle-url":"../node_modules/parcel/src/builtins/bundle-url.js"}],"../styles/atat.scss":[function(require,module,exports) {

var reloadCSS = require('_css_loader');
module.hot.dispose(reloadCSS);
module.hot.accept(reloadCSS);
},{"./../static/fonts/sourcesanspro-light-webfont.eot":[["sourcesanspro-light-webfont.134ae35c.eot","../static/fonts/sourcesanspro-light-webfont.eot"],"../static/fonts/sourcesanspro-light-webfont.eot"],"./../static/fonts/sourcesanspro-light-webfont.woff2":[["sourcesanspro-light-webfont.76235309.woff2","../static/fonts/sourcesanspro-light-webfont.woff2"],"../static/fonts/sourcesanspro-light-webfont.woff2"],"./../static/fonts/sourcesanspro-light-webfont.woff":[["sourcesanspro-light-webfont.7c8bcb0b.woff","../static/fonts/sourcesanspro-light-webfont.woff"],"../static/fonts/sourcesanspro-light-webfont.woff"],"./../static/fonts/sourcesanspro-light-webfont.ttf":[["sourcesanspro-light-webfont.18334c7e.ttf","../static/fonts/sourcesanspro-light-webfont.ttf"],"../static/fonts/sourcesanspro-light-webfont.ttf"],"./../static/fonts/sourcesanspro-regular-webfont.eot":[["sourcesanspro-regular-webfont.8b766abd.eot","../static/fonts/sourcesanspro-regular-webfont.eot"],"../static/fonts/sourcesanspro-regular-webfont.eot"],"./../static/fonts/sourcesanspro-regular-webfont.woff2":[["sourcesanspro-regular-webfont.4c124b38.woff2","../static/fonts/sourcesanspro-regular-webfont.woff2"],"../static/fonts/sourcesanspro-regular-webfont.woff2"],"./../static/fonts/sourcesanspro-regular-webfont.woff":[["sourcesanspro-regular-webfont.b0120280.woff","../static/fonts/sourcesanspro-regular-webfont.woff"],"../static/fonts/sourcesanspro-regular-webfont.woff"],"./../static/fonts/sourcesanspro-regular-webfont.ttf":[["sourcesanspro-regular-webfont.db7160ab.ttf","../static/fonts/sourcesanspro-regular-webfont.ttf"],"../static/fonts/sourcesanspro-regular-webfont.ttf"],"./../static/fonts/sourcesanspro-italic-webfont.eot":[["sourcesanspro-italic-webfont.945b0b26.eot","../static/fonts/sourcesanspro-italic-webfont.eot"],"../static/fonts/sourcesanspro-italic-webfont.eot"],"./../static/fonts/sourcesanspro-italic-webfont.woff2":[["sourcesanspro-italic-webfont.00ff8488.woff2","../static/fonts/sourcesanspro-italic-webfont.woff2"],"../static/fonts/sourcesanspro-italic-webfont.woff2"],"./../static/fonts/sourcesanspro-italic-webfont.woff":[["sourcesanspro-italic-webfont.d770ae84.woff","../static/fonts/sourcesanspro-italic-webfont.woff"],"../static/fonts/sourcesanspro-italic-webfont.woff"],"./../static/fonts/sourcesanspro-italic-webfont.ttf":[["sourcesanspro-italic-webfont.34c9ce16.ttf","../static/fonts/sourcesanspro-italic-webfont.ttf"],"../static/fonts/sourcesanspro-italic-webfont.ttf"],"./../static/fonts/sourcesanspro-bold-webfont.eot":[["sourcesanspro-bold-webfont.4c2fe9b5.eot","../static/fonts/sourcesanspro-bold-webfont.eot"],"../static/fonts/sourcesanspro-bold-webfont.eot"],"./../static/fonts/sourcesanspro-bold-webfont.woff2":[["sourcesanspro-bold-webfont.fe9344bb.woff2","../static/fonts/sourcesanspro-bold-webfont.woff2"],"../static/fonts/sourcesanspro-bold-webfont.woff2"],"./../static/fonts/sourcesanspro-bold-webfont.woff":[["sourcesanspro-bold-webfont.e3687139.woff","../static/fonts/sourcesanspro-bold-webfont.woff"],"../static/fonts/sourcesanspro-bold-webfont.woff"],"./../static/fonts/sourcesanspro-bold-webfont.ttf":[["sourcesanspro-bold-webfont.5faf684f.ttf","../static/fonts/sourcesanspro-bold-webfont.ttf"],"../static/fonts/sourcesanspro-bold-webfont.ttf"],"./../static/fonts/merriweather-light-webfont.eot":[["merriweather-light-webfont.5bc7f0e8.eot","../static/fonts/merriweather-light-webfont.eot"],"../static/fonts/merriweather-light-webfont.eot"],"./../static/fonts/merriweather-light-webfont.woff2":[["merriweather-light-webfont.1b1f32b7.woff2","../static/fonts/merriweather-light-webfont.woff2"],"../static/fonts/merriweather-light-webfont.woff2"],"./../static/fonts/merriweather-light-webfont.woff":[["merriweather-light-webfont.9845245a.woff","../static/fonts/merriweather-light-webfont.woff"],"../static/fonts/merriweather-light-webfont.woff"],"./../static/fonts/merriweather-light-webfont.ttf":[["merriweather-light-webfont.386fee9a.ttf","../static/fonts/merriweather-light-webfont.ttf"],"../static/fonts/merriweather-light-webfont.ttf"],"./../static/fonts/merriweather-regular-webfont.eot":[["merriweather-regular-webfont.a80f8324.eot","../static/fonts/merriweather-regular-webfont.eot"],"../static/fonts/merriweather-regular-webfont.eot"],"./../static/fonts/merriweather-regular-webfont.woff2":[["merriweather-regular-webfont.f71c61dd.woff2","../static/fonts/merriweather-regular-webfont.woff2"],"../static/fonts/merriweather-regular-webfont.woff2"],"./../static/fonts/merriweather-regular-webfont.woff":[["merriweather-regular-webfont.8338beec.woff","../static/fonts/merriweather-regular-webfont.woff"],"../static/fonts/merriweather-regular-webfont.woff"],"./../static/fonts/merriweather-regular-webfont.ttf":[["merriweather-regular-webfont.3661478a.ttf","../static/fonts/merriweather-regular-webfont.ttf"],"../static/fonts/merriweather-regular-webfont.ttf"],"./../static/fonts/merriweather-italic-webfont.eot":[["merriweather-italic-webfont.f3bdbf29.eot","../static/fonts/merriweather-italic-webfont.eot"],"../static/fonts/merriweather-italic-webfont.eot"],"./../static/fonts/merriweather-italic-webfont.woff2":[["merriweather-italic-webfont.6c56712c.woff2","../static/fonts/merriweather-italic-webfont.woff2"],"../static/fonts/merriweather-italic-webfont.woff2"],"./../static/fonts/merriweather-italic-webfont.woff":[["merriweather-italic-webfont.c64f21d1.woff","../static/fonts/merriweather-italic-webfont.woff"],"../static/fonts/merriweather-italic-webfont.woff"],"./../static/fonts/merriweather-italic-webfont.ttf":[["merriweather-italic-webfont.fc611bc9.ttf","../static/fonts/merriweather-italic-webfont.ttf"],"../static/fonts/merriweather-italic-webfont.ttf"],"./../static/fonts/merriweather-bold-webfont.eot":[["merriweather-bold-webfont.7ab8fe39.eot","../static/fonts/merriweather-bold-webfont.eot"],"../static/fonts/merriweather-bold-webfont.eot"],"./../static/fonts/merriweather-bold-webfont.woff2":[["merriweather-bold-webfont.3f042de9.woff2","../static/fonts/merriweather-bold-webfont.woff2"],"../static/fonts/merriweather-bold-webfont.woff2"],"./../static/fonts/merriweather-bold-webfont.woff":[["merriweather-bold-webfont.0391ff32.woff","../static/fonts/merriweather-bold-webfont.woff"],"../static/fonts/merriweather-bold-webfont.woff"],"./../static/fonts/merriweather-bold-webfont.ttf":[["merriweather-bold-webfont.523a75f1.ttf","../static/fonts/merriweather-bold-webfont.ttf"],"../static/fonts/merriweather-bold-webfont.ttf"],"./../static/img/arrow-both.png":[["arrow-both.4bb0bc24.png","../static/img/arrow-both.png"],"../static/img/arrow-both.png"],"./../static/img/arrow-both.svg":[["arrow-both.40570b7e.svg","../static/img/arrow-both.svg"],"../static/img/arrow-both.svg"],"./../static/img/correct8.png":[["correct8.a03d2fcf.png","../static/img/correct8.png"],"../static/img/correct8.png"],"./../static/img/correct8.svg":[["correct8.4e87f243.svg","../static/img/correct8.svg"],"../static/img/correct8.svg"],"./../static/img/external-link.png":[["external-link.7cc7907a.png","../static/img/external-link.png"],"../static/img/external-link.png"],"./../static/img/external-link.svg":[["external-link.0ba33f83.svg","../static/img/external-link.svg"],"../static/img/external-link.svg"],"./../static/img/external-link-hover.png":[["external-link-hover.0007810e.png","../static/img/external-link-hover.png"],"../static/img/external-link-hover.png"],"./../static/img/external-link-hover.svg":[["external-link-hover.e82acbc1.svg","../static/img/external-link-hover.svg"],"../static/img/external-link-hover.svg"],"./../static/img/external-link-alt.png":[["external-link-alt.410f199e.png","../static/img/external-link-alt.png"],"../static/img/external-link-alt.png"],"./../static/img/external-link-alt.svg":[["external-link-alt.f8c085df.svg","../static/img/external-link-alt.svg"],"../static/img/external-link-alt.svg"],"./../static/img/external-link-alt-hover.png":[["external-link-alt-hover.fe210d33.png","../static/img/external-link-alt-hover.png"],"../static/img/external-link-alt-hover.png"],"./../static/img/external-link-alt-hover.svg":[["external-link-alt-hover.720d3de5.svg","../static/img/external-link-alt-hover.svg"],"../static/img/external-link-alt-hover.svg"],"./../static/img/minus.png":[["minus.71f0755b.png","../static/img/minus.png"],"../static/img/minus.png"],"./../static/img/minus.svg":[["minus.30f190d9.svg","../static/img/minus.svg"],"../static/img/minus.svg"],"./../static/img/plus.png":[["plus.31113133.png","../static/img/plus.png"],"../static/img/plus.png"],"./../static/img/plus.svg":[["plus.7ceba975.svg","../static/img/plus.svg"],"../static/img/plus.svg"],"./../static/img/alerts/success.png":[["success.4e032499.png","../static/img/alerts/success.png"],"../static/img/alerts/success.png"],"./../static/img/alerts/success.svg":[["success.9ef06b70.svg","../static/img/alerts/success.svg"],"../static/img/alerts/success.svg"],"./../static/img/alerts/warning.png":[["warning.9253aad8.png","../static/img/alerts/warning.png"],"../static/img/alerts/warning.png"],"./../static/img/alerts/warning.svg":[["warning.bde34fef.svg","../static/img/alerts/warning.svg"],"../static/img/alerts/warning.svg"],"./../static/img/alerts/error.png":[["error.77a47b7b.png","../static/img/alerts/error.png"],"../static/img/alerts/error.png"],"./../static/img/alerts/error.svg":[["error.fed7fc9a.svg","../static/img/alerts/error.svg"],"../static/img/alerts/error.svg"],"./../static/img/alerts/info.png":[["info.6946b1ae.png","../static/img/alerts/info.png"],"../static/img/alerts/info.png"],"./../static/img/alerts/info.svg":[["info.65032fa3.svg","../static/img/alerts/info.svg"],"../static/img/alerts/info.svg"],"./../static/img/angle-arrow-down-primary.png":[["angle-arrow-down-primary.ab8d4776.png","../static/img/angle-arrow-down-primary.png"],"../static/img/angle-arrow-down-primary.png"],"./../static/img/angle-arrow-down-primary.svg":[["angle-arrow-down-primary.1c0886c7.svg","../static/img/angle-arrow-down-primary.svg"],"../static/img/angle-arrow-down-primary.svg"],"./../static/img/angle-arrow-down-primary-hover.png":[["angle-arrow-down-primary-hover.d936067e.png","../static/img/angle-arrow-down-primary-hover.png"],"../static/img/angle-arrow-down-primary-hover.png"],"./../static/img/angle-arrow-down-primary-hover.svg":[["angle-arrow-down-primary-hover.11d98d2a.svg","../static/img/angle-arrow-down-primary-hover.svg"],"../static/img/angle-arrow-down-primary-hover.svg"],"./../static/img/close.png":[["close.707c1f41.png","../static/img/close.png"],"../static/img/close.png"],"./../static/img/close.svg":[["close.34c66938.svg","../static/img/close.svg"],"../static/img/close.svg"],"./../static/img/angle-arrow-up-primary.png":[["angle-arrow-up-primary.fd1251b8.png","../static/img/angle-arrow-up-primary.png"],"../static/img/angle-arrow-up-primary.png"],"./../static/img/angle-arrow-up-primary.svg":[["angle-arrow-up-primary.b38f7f9a.svg","../static/img/angle-arrow-up-primary.svg"],"../static/img/angle-arrow-up-primary.svg"],"./../static/img/angle-arrow-up-primary-hover.png":[["angle-arrow-up-primary-hover.87ccb668.png","../static/img/angle-arrow-up-primary-hover.png"],"../static/img/angle-arrow-up-primary-hover.png"],"./../static/img/angle-arrow-up-primary-hover.svg":[["angle-arrow-up-primary-hover.656ab109.svg","../static/img/angle-arrow-up-primary-hover.svg"],"../static/img/angle-arrow-up-primary-hover.svg"],"./../static/img/arrow-down.png":[["arrow-down.188ad70b.png","../static/img/arrow-down.png"],"../static/img/arrow-down.png"],"./../static/img/arrow-down.svg":[["arrow-down.08222248.svg","../static/img/arrow-down.svg"],"../static/img/arrow-down.svg"],"./../static/img/arrow-right.png":[["arrow-right.c5e6e18a.png","../static/img/arrow-right.png"],"../static/img/arrow-right.png"],"./../static/img/arrow-right.svg":[["arrow-right.8dc15dc6.svg","../static/img/arrow-right.svg"],"../static/img/arrow-right.svg"],"./../static/img/social-icons/png/facebook25.png":[["facebook25.e89f66fb.png","../static/img/social-icons/png/facebook25.png"],"../static/img/social-icons/png/facebook25.png"],"./../static/img/social-icons/svg/facebook25.svg":[["facebook25.0247732a.svg","../static/img/social-icons/svg/facebook25.svg"],"../static/img/social-icons/svg/facebook25.svg"],"./../static/img/social-icons/png/twitter16.png":[["twitter16.33fbe6bc.png","../static/img/social-icons/png/twitter16.png"],"../static/img/social-icons/png/twitter16.png"],"./../static/img/social-icons/svg/twitter16.svg":[["twitter16.27cfc1cf.svg","../static/img/social-icons/svg/twitter16.svg"],"../static/img/social-icons/svg/twitter16.svg"],"./../static/img/social-icons/png/youtube15.png":[["youtube15.8e97452a.png","../static/img/social-icons/png/youtube15.png"],"../static/img/social-icons/png/youtube15.png"],"./../static/img/social-icons/svg/youtube15.svg":[["youtube15.e0b05878.svg","../static/img/social-icons/svg/youtube15.svg"],"../static/img/social-icons/svg/youtube15.svg"],"./../static/img/social-icons/png/rss25.png":[["rss25.87d6c4ef.png","../static/img/social-icons/png/rss25.png"],"../static/img/social-icons/png/rss25.png"],"./../static/img/social-icons/svg/rss25.svg":[["rss25.f5125cc9.svg","../static/img/social-icons/svg/rss25.svg"],"../static/img/social-icons/svg/rss25.svg"],"./../static/img/correct9.png":[["correct9.860cef73.png","../static/img/correct9.png"],"../static/img/correct9.png"],"./../static/img/correct9.svg":[["correct9.f5b58d71.svg","../static/img/correct9.svg"],"../static/img/correct9.svg"],"./../static/img/hero.png":[["hero.1d4e1843.png","../static/img/hero.png"],"../static/img/hero.png"],"./../static/img/plus-alt.png":[["plus-alt.ce2ceab2.png","../static/img/plus-alt.png"],"../static/img/plus-alt.png"],"./../static/img/plus-alt.svg":[["plus-alt.3bdfe660.svg","../static/img/plus-alt.svg"],"../static/img/plus-alt.svg"],"./../static/img/angle-arrow-down.png":[["angle-arrow-down.eaf9b383.png","../static/img/angle-arrow-down.png"],"../static/img/angle-arrow-down.png"],"./../static/img/angle-arrow-down.svg":[["angle-arrow-down.da471750.svg","../static/img/angle-arrow-down.svg"],"../static/img/angle-arrow-down.svg"],"./../static/img/minus-alt.png":[["minus-alt.4aa24c1e.png","../static/img/minus-alt.png"],"../static/img/minus-alt.png"],"./../static/img/minus-alt.svg":[["minus-alt.a3fdb328.svg","../static/img/minus-alt.svg"],"../static/img/minus-alt.svg"],"./../static/img/angle-arrow-down-hover.png":[["angle-arrow-down-hover.baa52fa9.png","../static/img/angle-arrow-down-hover.png"],"../static/img/angle-arrow-down-hover.png"],"./../static/img/angle-arrow-down-hover.svg":[["angle-arrow-down-hover.9cc540eb.svg","../static/img/angle-arrow-down-hover.svg"],"../static/img/angle-arrow-down-hover.svg"],"./../static/img/search-alt.png":[["search-alt.6266295c.png","../static/img/search-alt.png"],"../static/img/search-alt.png"],"./../static/img/search-alt.svg":[["search-alt.3ad0b1db.svg","../static/img/search-alt.svg"],"../static/img/search-alt.svg"],"./../static/img/search.png":[["search.5416b9aa.png","../static/img/search.png"],"../static/img/search.png"],"./../static/img/search.svg":[["search.ea14b3f4.svg","../static/img/search.svg"],"../static/img/search.svg"],"./../static/icons/checkmark.svg":[["checkmark.13582669.svg","../static/icons/checkmark.svg"],"../static/icons/checkmark.svg"],"./../static/icons/search.svg":[["search.51c3965a.svg","../static/icons/search.svg"],"../static/icons/search.svg"],"_css_loader":"../node_modules/parcel/src/builtins/css-loader.js"}],"thing.js":[function(require,module,exports) {
console.log('hanlo again');
window.onload = function () {
  console.log('boop');
  var thing = document.querySelector('#hello');
  thing.innerHTML = 'hanlo friendo';
};
},{}],"index.js":[function(require,module,exports) {
'use strict';

var _atat = require('../styles/atat.scss');

var _atat2 = _interopRequireDefault(_atat);

require('./thing');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

console.log('hellooooo');
},{"../styles/atat.scss":"../styles/atat.scss","./thing":"thing.js"}],"../node_modules/parcel/src/builtins/hmr-runtime.js":[function(require,module,exports) {
var global = arguments[3];
var OVERLAY_ID = '__parcel__error__overlay__';

var OldModule = module.bundle.Module;

function Module(moduleName) {
  OldModule.call(this, moduleName);
  this.hot = {
    data: module.bundle.hotData,
    _acceptCallbacks: [],
    _disposeCallbacks: [],
    accept: function (fn) {
      this._acceptCallbacks.push(fn || function () {});
    },
    dispose: function (fn) {
      this._disposeCallbacks.push(fn);
    }
  };

  module.bundle.hotData = null;
}

module.bundle.Module = Module;

var parent = module.bundle.parent;
if ((!parent || !parent.isParcelRequire) && typeof WebSocket !== 'undefined') {
  var hostname = '' || location.hostname;
  var protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  var ws = new WebSocket(protocol + '://' + hostname + ':' + '63392' + '/');
  ws.onmessage = function (event) {
    var data = JSON.parse(event.data);

    if (data.type === 'update') {
      console.clear();

      data.assets.forEach(function (asset) {
        hmrApply(global.parcelRequire, asset);
      });

      data.assets.forEach(function (asset) {
        if (!asset.isNew) {
          hmrAccept(global.parcelRequire, asset.id);
        }
      });
    }

    if (data.type === 'reload') {
      ws.close();
      ws.onclose = function () {
        location.reload();
      };
    }

    if (data.type === 'error-resolved') {
      console.log('[parcel] ✨ Error resolved');

      removeErrorOverlay();
    }

    if (data.type === 'error') {
      console.error('[parcel] 🚨  ' + data.error.message + '\n' + data.error.stack);

      removeErrorOverlay();

      var overlay = createErrorOverlay(data);
      document.body.appendChild(overlay);
    }
  };
}

function removeErrorOverlay() {
  var overlay = document.getElementById(OVERLAY_ID);
  if (overlay) {
    overlay.remove();
  }
}

function createErrorOverlay(data) {
  var overlay = document.createElement('div');
  overlay.id = OVERLAY_ID;

  // html encode message and stack trace
  var message = document.createElement('div');
  var stackTrace = document.createElement('pre');
  message.innerText = data.error.message;
  stackTrace.innerText = data.error.stack;

  overlay.innerHTML = '<div style="background: black; font-size: 16px; color: white; position: fixed; height: 100%; width: 100%; top: 0px; left: 0px; padding: 30px; opacity: 0.85; font-family: Menlo, Consolas, monospace; z-index: 9999;">' + '<span style="background: red; padding: 2px 4px; border-radius: 2px;">ERROR</span>' + '<span style="top: 2px; margin-left: 5px; position: relative;">🚨</span>' + '<div style="font-size: 18px; font-weight: bold; margin-top: 20px;">' + message.innerHTML + '</div>' + '<pre>' + stackTrace.innerHTML + '</pre>' + '</div>';

  return overlay;
}

function getParents(bundle, id) {
  var modules = bundle.modules;
  if (!modules) {
    return [];
  }

  var parents = [];
  var k, d, dep;

  for (k in modules) {
    for (d in modules[k][1]) {
      dep = modules[k][1][d];
      if (dep === id || Array.isArray(dep) && dep[dep.length - 1] === id) {
        parents.push(k);
      }
    }
  }

  if (bundle.parent) {
    parents = parents.concat(getParents(bundle.parent, id));
  }

  return parents;
}

function hmrApply(bundle, asset) {
  var modules = bundle.modules;
  if (!modules) {
    return;
  }

  if (modules[asset.id] || !bundle.parent) {
    var fn = new Function('require', 'module', 'exports', asset.generated.js);
    asset.isNew = !modules[asset.id];
    modules[asset.id] = [fn, asset.deps];
  } else if (bundle.parent) {
    hmrApply(bundle.parent, asset);
  }
}

function hmrAccept(bundle, id) {
  var modules = bundle.modules;
  if (!modules) {
    return;
  }

  if (!modules[id] && bundle.parent) {
    return hmrAccept(bundle.parent, id);
  }

  var cached = bundle.cache[id];
  bundle.hotData = {};
  if (cached) {
    cached.hot.data = bundle.hotData;
  }

  if (cached && cached.hot && cached.hot._disposeCallbacks.length) {
    cached.hot._disposeCallbacks.forEach(function (cb) {
      cb(bundle.hotData);
    });
  }

  delete bundle.cache[id];
  bundle(id);

  cached = bundle.cache[id];
  if (cached && cached.hot && cached.hot._acceptCallbacks.length) {
    cached.hot._acceptCallbacks.forEach(function (cb) {
      cb();
    });
    return true;
  }

  return getParents(global.parcelRequire, id).some(function (id) {
    return hmrAccept(global.parcelRequire, id);
  });
}
},{}]},{},["../node_modules/parcel/src/builtins/hmr-runtime.js","index.js"], null)
//# sourceMappingURL=/index.map