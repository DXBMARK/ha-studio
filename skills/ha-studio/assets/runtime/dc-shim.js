/* dc-shim.js — tiny, dependency-free runtime that renders the <x-dc> design-component
   templates (sc-for / sc-if / {{ holes }}) in any browser, so previews and screenshots
   work outside Claude Design. (c) 2026 DXBMARK LLC — Apache-2.0 */
(function () {
  var HOLE = /\{\{\s*([^}]+?)\s*\}\}/g;
  var WHOLE = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/;
  function lookup(path, scopes) {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    var parts = path.split('.'), v, i;
    for (i = scopes.length - 1; i >= 0; i--) {
      if (parts[0] in scopes[i]) { v = scopes[i][parts[0]]; break; }
    }
    for (i = 1; i < parts.length && v != null; i++) v = v[parts[i]];
    return v;
  }
  function interp(str, scopes) {
    return str.replace(HOLE, function (_, p) { var v = lookup(p, scopes); return v == null ? '' : String(v); });
  }
  function render(node, scopes, parent) {
    if (node.nodeType === 3) { parent.appendChild(document.createTextNode(interp(node.nodeValue, scopes))); return; }
    if (node.nodeType !== 1) return;
    var tag = node.tagName.toLowerCase(), kids = Array.prototype.slice.call(node.childNodes);
    if (tag === 'helmet') return;
    if (tag === 'sc-for') {
      var m = (node.getAttribute('list') || '').match(WHOLE);
      var list = (m && lookup(m[1], scopes)) || [], as = node.getAttribute('as');
      list.forEach(function (item) {
        var sc = {}; sc[as] = item; var next = scopes.concat([sc]);
        kids.forEach(function (c) { render(c, next, parent); });
      });
      return;
    }
    if (tag === 'sc-if') {
      var mm = (node.getAttribute('value') || '').match(WHOLE);
      if (mm && lookup(mm[1], scopes)) kids.forEach(function (c) { render(c, scopes, parent); });
      return;
    }
    var el = node.cloneNode(false);
    Array.prototype.slice.call(node.attributes).forEach(function (a) {
      var name = a.name, val = a.value;
      if (/^on/i.test(name)) {
        el.removeAttribute(name);
        var w = val.match(WHOLE), fn = w && lookup(w[1], scopes);
        if (typeof fn === 'function') el.addEventListener(name.slice(2).toLowerCase(), fn);
        return;
      }
      if (val.indexOf('{{') > -1) el.setAttribute(name, interp(val, scopes));
    });
    kids.forEach(function (c) { render(c, scopes, el); });
    parent.appendChild(el);
  }
  function boot() {
    var host = document.querySelector('x-dc');
    var scriptEl = document.querySelector('script[data-dc-script]');
    if (!host || !scriptEl) return;
    var helmet = host.querySelector('helmet');
    if (helmet) Array.prototype.slice.call(helmet.children).forEach(function (c) { document.head.appendChild(c.cloneNode(true)); });
    var tpl = host.cloneNode(true);
    var props = {};
    try { props = JSON.parse(scriptEl.getAttribute('data-props') || '{}'); } catch (e) {}
    function DCLogic(p) { this.props = p || {}; this.state = {}; }
    DCLogic.prototype.setState = function (patch) {
      var next = typeof patch === 'function' ? patch(this.state) : patch;
      for (var k in next) this.state[k] = next[k];
      paint();
    };
    window.DCLogic = DCLogic;
    var Component = new Function(scriptEl.textContent + '\nreturn Component;')();
    var inst = new Component(props);
    var root = document.createElement('div');
    root.id = 'dc-root';
    host.parentNode.insertBefore(root, host);
    host.style.display = 'none';
    function paint() {
      var scrolls = Array.prototype.map.call(root.querySelectorAll('*'), function (e) { return e.scrollTop; });
      var vals = inst.renderVals(), frag = document.createDocumentFragment();
      Array.prototype.slice.call(tpl.childNodes).forEach(function (c) { render(c, [vals], frag); });
      root.textContent = '';
      root.appendChild(frag);
      Array.prototype.forEach.call(root.querySelectorAll('*'), function (e, i) { if (scrolls[i]) e.scrollTop = scrolls[i]; });
    }
    window.__dcRepaint = paint;
    window.__dc = inst;
    paint();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
