//#region node_modules/@lit/reactive-element/css-tag.js
var e = globalThis, t = e.ShadowRoot && (e.ShadyCSS === void 0 || e.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, n = Symbol(), r = /* @__PURE__ */ new WeakMap(), i = class {
	constructor(e, t, r) {
		if (this._$cssResult$ = !0, r !== n) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
		this.cssText = e, this.t = t;
	}
	get styleSheet() {
		let e = this.o, n = this.t;
		if (t && e === void 0) {
			let t = n !== void 0 && n.length === 1;
			t && (e = r.get(n)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), t && r.set(n, e));
		}
		return e;
	}
	toString() {
		return this.cssText;
	}
}, a = (e) => new i(typeof e == "string" ? e : e + "", void 0, n), o = (e, ...t) => new i(e.length === 1 ? e[0] : t.reduce((t, n, r) => t + ((e) => {
	if (!0 === e._$cssResult$) return e.cssText;
	if (typeof e == "number") return e;
	throw Error("Value passed to 'css' function must be a 'css' function result: " + e + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
})(n) + e[r + 1], e[0]), e, n), s = (n, r) => {
	if (t) n.adoptedStyleSheets = r.map((e) => e instanceof CSSStyleSheet ? e : e.styleSheet);
	else for (let t of r) {
		let r = document.createElement("style"), i = e.litNonce;
		i !== void 0 && r.setAttribute("nonce", i), r.textContent = t.cssText, n.appendChild(r);
	}
}, c = t ? (e) => e : (e) => e instanceof CSSStyleSheet ? ((e) => {
	let t = "";
	for (let n of e.cssRules) t += n.cssText;
	return a(t);
})(e) : e, { is: l, defineProperty: u, getOwnPropertyDescriptor: d, getOwnPropertyNames: f, getOwnPropertySymbols: p, getPrototypeOf: m } = Object, h = globalThis, ee = h.trustedTypes, te = ee ? ee.emptyScript : "", ne = h.reactiveElementPolyfillSupport, g = (e, t) => e, _ = {
	toAttribute(e, t) {
		switch (t) {
			case Boolean:
				e = e ? te : null;
				break;
			case Object:
			case Array: e = e == null ? e : JSON.stringify(e);
		}
		return e;
	},
	fromAttribute(e, t) {
		let n = e;
		switch (t) {
			case Boolean:
				n = e !== null;
				break;
			case Number:
				n = e === null ? null : Number(e);
				break;
			case Object:
			case Array: try {
				n = JSON.parse(e);
			} catch {
				n = null;
			}
		}
		return n;
	}
}, re = (e, t) => !l(e, t), ie = {
	attribute: !0,
	type: String,
	converter: _,
	reflect: !1,
	useDefault: !1,
	hasChanged: re
};
Symbol.metadata ??= Symbol("metadata"), h.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
var v = class extends HTMLElement {
	static addInitializer(e) {
		this._$Ei(), (this.l ??= []).push(e);
	}
	static get observedAttributes() {
		return this.finalize(), this._$Eh && [...this._$Eh.keys()];
	}
	static createProperty(e, t = ie) {
		if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
			let n = Symbol(), r = this.getPropertyDescriptor(e, n, t);
			r !== void 0 && u(this.prototype, e, r);
		}
	}
	static getPropertyDescriptor(e, t, n) {
		let { get: r, set: i } = d(this.prototype, e) ?? {
			get() {
				return this[t];
			},
			set(e) {
				this[t] = e;
			}
		};
		return {
			get: r,
			set(t) {
				let a = r?.call(this);
				i?.call(this, t), this.requestUpdate(e, a, n);
			},
			configurable: !0,
			enumerable: !0
		};
	}
	static getPropertyOptions(e) {
		return this.elementProperties.get(e) ?? ie;
	}
	static _$Ei() {
		if (this.hasOwnProperty(g("elementProperties"))) return;
		let e = m(this);
		e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
	}
	static finalize() {
		if (this.hasOwnProperty(g("finalized"))) return;
		if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(g("properties"))) {
			let e = this.properties, t = [...f(e), ...p(e)];
			for (let n of t) this.createProperty(n, e[n]);
		}
		let e = this[Symbol.metadata];
		if (e !== null) {
			let t = litPropertyMetadata.get(e);
			if (t !== void 0) for (let [e, n] of t) this.elementProperties.set(e, n);
		}
		this._$Eh = /* @__PURE__ */ new Map();
		for (let [e, t] of this.elementProperties) {
			let n = this._$Eu(e, t);
			n !== void 0 && this._$Eh.set(n, e);
		}
		this.elementStyles = this.finalizeStyles(this.styles);
	}
	static finalizeStyles(e) {
		let t = [];
		if (Array.isArray(e)) {
			let n = new Set(e.flat(1 / 0).reverse());
			for (let e of n) t.unshift(c(e));
		} else e !== void 0 && t.push(c(e));
		return t;
	}
	static _$Eu(e, t) {
		let n = t.attribute;
		return !1 === n ? void 0 : typeof n == "string" ? n : typeof e == "string" ? e.toLowerCase() : void 0;
	}
	constructor() {
		super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
	}
	_$Ev() {
		this._$ES = new Promise((e) => this.enableUpdating = e), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((e) => e(this));
	}
	addController(e) {
		(this._$EO ??= /* @__PURE__ */ new Set()).add(e), this.renderRoot !== void 0 && this.isConnected && e.hostConnected?.();
	}
	removeController(e) {
		this._$EO?.delete(e);
	}
	_$E_() {
		let e = /* @__PURE__ */ new Map(), t = this.constructor.elementProperties;
		for (let n of t.keys()) this.hasOwnProperty(n) && (e.set(n, this[n]), delete this[n]);
		e.size > 0 && (this._$Ep = e);
	}
	createRenderRoot() {
		let e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
		return s(e, this.constructor.elementStyles), e;
	}
	connectedCallback() {
		this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(!0), this._$EO?.forEach((e) => e.hostConnected?.());
	}
	enableUpdating(e) {}
	disconnectedCallback() {
		this._$EO?.forEach((e) => e.hostDisconnected?.());
	}
	attributeChangedCallback(e, t, n) {
		this._$AK(e, n);
	}
	_$ET(e, t) {
		let n = this.constructor.elementProperties.get(e), r = this.constructor._$Eu(e, n);
		if (r !== void 0 && !0 === n.reflect) {
			let i = (n.converter?.toAttribute === void 0 ? _ : n.converter).toAttribute(t, n.type);
			this._$Em = e, i == null ? this.removeAttribute(r) : this.setAttribute(r, i), this._$Em = null;
		}
	}
	_$AK(e, t) {
		let n = this.constructor, r = n._$Eh.get(e);
		if (r !== void 0 && this._$Em !== r) {
			let e = n.getPropertyOptions(r), i = typeof e.converter == "function" ? { fromAttribute: e.converter } : e.converter?.fromAttribute === void 0 ? _ : e.converter;
			this._$Em = r;
			let a = i.fromAttribute(t, e.type);
			this[r] = a ?? this._$Ej?.get(r) ?? a, this._$Em = null;
		}
	}
	requestUpdate(e, t, n, r = !1, i) {
		if (e !== void 0) {
			let a = this.constructor;
			if (!1 === r && (i = this[e]), n ??= a.getPropertyOptions(e), !((n.hasChanged ?? re)(i, t) || n.useDefault && n.reflect && i === this._$Ej?.get(e) && !this.hasAttribute(a._$Eu(e, n)))) return;
			this.C(e, t, n);
		}
		!1 === this.isUpdatePending && (this._$ES = this._$EP());
	}
	C(e, t, { useDefault: n, reflect: r, wrapped: i }, a) {
		n && !(this._$Ej ??= /* @__PURE__ */ new Map()).has(e) && (this._$Ej.set(e, a ?? t ?? this[e]), !0 !== i || a !== void 0) || (this._$AL.has(e) || (this.hasUpdated || n || (t = void 0), this._$AL.set(e, t)), !0 === r && this._$Em !== e && (this._$Eq ??= /* @__PURE__ */ new Set()).add(e));
	}
	async _$EP() {
		this.isUpdatePending = !0;
		try {
			await this._$ES;
		} catch (e) {
			Promise.reject(e);
		}
		let e = this.scheduleUpdate();
		return e != null && await e, !this.isUpdatePending;
	}
	scheduleUpdate() {
		return this.performUpdate();
	}
	performUpdate() {
		if (!this.isUpdatePending) return;
		if (!this.hasUpdated) {
			if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
				for (let [e, t] of this._$Ep) this[e] = t;
				this._$Ep = void 0;
			}
			let e = this.constructor.elementProperties;
			if (e.size > 0) for (let [t, n] of e) {
				let { wrapped: e } = n, r = this[t];
				!0 !== e || this._$AL.has(t) || r === void 0 || this.C(t, void 0, n, r);
			}
		}
		let e = !1, t = this._$AL;
		try {
			e = this.shouldUpdate(t), e ? (this.willUpdate(t), this._$EO?.forEach((e) => e.hostUpdate?.()), this.update(t)) : this._$EM();
		} catch (t) {
			throw e = !1, this._$EM(), t;
		}
		e && this._$AE(t);
	}
	willUpdate(e) {}
	_$AE(e) {
		this._$EO?.forEach((e) => e.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
	}
	_$EM() {
		this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
	}
	get updateComplete() {
		return this.getUpdateComplete();
	}
	getUpdateComplete() {
		return this._$ES;
	}
	shouldUpdate(e) {
		return !0;
	}
	update(e) {
		this._$Eq &&= this._$Eq.forEach((e) => this._$ET(e, this[e])), this._$EM();
	}
	updated(e) {}
	firstUpdated(e) {}
};
v.elementStyles = [], v.shadowRootOptions = { mode: "open" }, v[g("elementProperties")] = /* @__PURE__ */ new Map(), v[g("finalized")] = /* @__PURE__ */ new Map(), ne?.({ ReactiveElement: v }), (h.reactiveElementVersions ??= []).push("2.1.2");
//#endregion
//#region node_modules/lit-html/lit-html.js
var y = globalThis, ae = (e) => e, b = y.trustedTypes, oe = b ? b.createPolicy("lit-html", { createHTML: (e) => e }) : void 0, se = "$lit$", x = `lit$${Math.random().toFixed(9).slice(2)}$`, S = "?" + x, ce = `<${S}>`, C = document, w = () => C.createComment(""), T = (e) => e === null || typeof e != "object" && typeof e != "function", E = Array.isArray, le = (e) => E(e) || typeof e?.[Symbol.iterator] == "function", D = "[ 	\n\f\r]", O = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, ue = /-->/g, de = />/g, k = RegExp(`>|${D}(?:([^\\s"'>=/]+)(${D}*=${D}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"), fe = /'/g, pe = /"/g, me = /^(?:script|style|textarea|title)$/i, he = (e) => (t, ...n) => ({
	_$litType$: e,
	strings: t,
	values: n
}), A = he(1), j = he(2), M = Symbol.for("lit-noChange"), N = Symbol.for("lit-nothing"), ge = /* @__PURE__ */ new WeakMap(), P = C.createTreeWalker(C, 129);
function _e(e, t) {
	if (!E(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
	return oe === void 0 ? t : oe.createHTML(t);
}
var ve = (e, t) => {
	let n = e.length - 1, r = [], i, a = t === 2 ? "<svg>" : t === 3 ? "<math>" : "", o = O;
	for (let t = 0; t < n; t++) {
		let n = e[t], s, c, l = -1, u = 0;
		for (; u < n.length && (o.lastIndex = u, c = o.exec(n), c !== null);) u = o.lastIndex, o === O ? c[1] === "!--" ? o = ue : c[1] === void 0 ? c[2] === void 0 ? c[3] !== void 0 && (o = k) : (me.test(c[2]) && (i = RegExp("</" + c[2], "g")), o = k) : o = de : o === k ? c[0] === ">" ? (o = i ?? O, l = -1) : c[1] === void 0 ? l = -2 : (l = o.lastIndex - c[2].length, s = c[1], o = c[3] === void 0 ? k : c[3] === "\"" ? pe : fe) : o === pe || o === fe ? o = k : o === ue || o === de ? o = O : (o = k, i = void 0);
		let d = o === k && e[t + 1].startsWith("/>") ? " " : "";
		a += o === O ? n + ce : l >= 0 ? (r.push(s), n.slice(0, l) + se + n.slice(l) + x + d) : n + x + (l === -2 ? t : d);
	}
	return [_e(e, a + (e[n] || "<?>") + (t === 2 ? "</svg>" : t === 3 ? "</math>" : "")), r];
}, F = class e {
	constructor({ strings: t, _$litType$: n }, r) {
		let i;
		this.parts = [];
		let a = 0, o = 0, s = t.length - 1, c = this.parts, [l, u] = ve(t, n);
		if (this.el = e.createElement(l, r), P.currentNode = this.el.content, n === 2 || n === 3) {
			let e = this.el.content.firstChild;
			e.replaceWith(...e.childNodes);
		}
		for (; (i = P.nextNode()) !== null && c.length < s;) {
			if (i.nodeType === 1) {
				if (i.hasAttributes()) for (let e of i.getAttributeNames()) if (e.endsWith(se)) {
					let t = u[o++], n = i.getAttribute(e).split(x), r = /([.?@])?(.*)/.exec(t);
					c.push({
						type: 1,
						index: a,
						name: r[2],
						strings: n,
						ctor: r[1] === "." ? be : r[1] === "?" ? xe : r[1] === "@" ? Se : R
					}), i.removeAttribute(e);
				} else e.startsWith(x) && (c.push({
					type: 6,
					index: a
				}), i.removeAttribute(e));
				if (me.test(i.tagName)) {
					let e = i.textContent.split(x), t = e.length - 1;
					if (t > 0) {
						i.textContent = b ? b.emptyScript : "";
						for (let n = 0; n < t; n++) i.append(e[n], w()), P.nextNode(), c.push({
							type: 2,
							index: ++a
						});
						i.append(e[t], w());
					}
				}
			} else if (i.nodeType === 8) {
				if (i.data === S) c.push({
					type: 2,
					index: a
				});
				else {
					let e = -1;
					for (; (e = i.data.indexOf(x, e + 1)) !== -1;) c.push({
						type: 7,
						index: a
					}), e += x.length - 1;
				}
			}
			a++;
		}
	}
	static createElement(e, t) {
		let n = C.createElement("template");
		return n.innerHTML = e, n;
	}
};
function I(e, t, n = e, r) {
	if (t === M) return t;
	let i = r === void 0 ? n._$Cl : n._$Co?.[r], a = T(t) ? void 0 : t._$litDirective$;
	return i?.constructor !== a && (i?._$AO?.(!1), a === void 0 ? i = void 0 : (i = new a(e), i._$AT(e, n, r)), r === void 0 ? n._$Cl = i : (n._$Co ??= [])[r] = i), i !== void 0 && (t = I(e, i._$AS(e, t.values), i, r)), t;
}
var ye = class {
	constructor(e, t) {
		this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
	}
	get parentNode() {
		return this._$AM.parentNode;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	u(e) {
		let { el: { content: t }, parts: n } = this._$AD, r = (e?.creationScope ?? C).importNode(t, !0);
		P.currentNode = r;
		let i = P.nextNode(), a = 0, o = 0, s = n[0];
		for (; s !== void 0;) {
			if (a === s.index) {
				let t;
				s.type === 2 ? t = new L(i, i.nextSibling, this, e) : s.type === 1 ? t = new s.ctor(i, s.name, s.strings, this, e) : s.type === 6 && (t = new Ce(i, this, e)), this._$AV.push(t), s = n[++o];
			}
			a !== s?.index && (i = P.nextNode(), a++);
		}
		return P.currentNode = C, r;
	}
	p(e) {
		let t = 0;
		for (let n of this._$AV) n !== void 0 && (n.strings === void 0 ? n._$AI(e[t]) : (n._$AI(e, n, t), t += n.strings.length - 2)), t++;
	}
}, L = class e {
	get _$AU() {
		return this._$AM?._$AU ?? this._$Cv;
	}
	constructor(e, t, n, r) {
		this.type = 2, this._$AH = N, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = n, this.options = r, this._$Cv = r?.isConnected ?? !0;
	}
	get parentNode() {
		let e = this._$AA.parentNode, t = this._$AM;
		return t !== void 0 && e?.nodeType === 11 && (e = t.parentNode), e;
	}
	get startNode() {
		return this._$AA;
	}
	get endNode() {
		return this._$AB;
	}
	_$AI(e, t = this) {
		e = I(this, e, t), T(e) ? e === N || e == null || e === "" ? (this._$AH !== N && this._$AR(), this._$AH = N) : e !== this._$AH && e !== M && this._(e) : e._$litType$ === void 0 ? e.nodeType === void 0 ? le(e) ? this.k(e) : this._(e) : this.T(e) : this.$(e);
	}
	O(e) {
		return this._$AA.parentNode.insertBefore(e, this._$AB);
	}
	T(e) {
		this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
	}
	_(e) {
		this._$AH !== N && T(this._$AH) ? this._$AA.nextSibling.data = e : this.T(C.createTextNode(e)), this._$AH = e;
	}
	$(e) {
		let { values: t, _$litType$: n } = e, r = typeof n == "number" ? this._$AC(e) : (n.el === void 0 && (n.el = F.createElement(_e(n.h, n.h[0]), this.options)), n);
		if (this._$AH?._$AD === r) this._$AH.p(t);
		else {
			let e = new ye(r, this), n = e.u(this.options);
			e.p(t), this.T(n), this._$AH = e;
		}
	}
	_$AC(e) {
		let t = ge.get(e.strings);
		return t === void 0 && ge.set(e.strings, t = new F(e)), t;
	}
	k(t) {
		E(this._$AH) || (this._$AH = [], this._$AR());
		let n = this._$AH, r, i = 0;
		for (let a of t) i === n.length ? n.push(r = new e(this.O(w()), this.O(w()), this, this.options)) : r = n[i], r._$AI(a), i++;
		i < n.length && (this._$AR(r && r._$AB.nextSibling, i), n.length = i);
	}
	_$AR(e = this._$AA.nextSibling, t) {
		for (this._$AP?.(!1, !0, t); e !== this._$AB;) {
			let t = ae(e).nextSibling;
			ae(e).remove(), e = t;
		}
	}
	setConnected(e) {
		this._$AM === void 0 && (this._$Cv = e, this._$AP?.(e));
	}
}, R = class {
	get tagName() {
		return this.element.tagName;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	constructor(e, t, n, r, i) {
		this.type = 1, this._$AH = N, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = i, n.length > 2 || n[0] !== "" || n[1] !== "" ? (this._$AH = Array(n.length - 1).fill(/* @__PURE__ */ new String()), this.strings = n) : this._$AH = N;
	}
	_$AI(e, t = this, n, r) {
		let i = this.strings, a = !1;
		if (i === void 0) e = I(this, e, t, 0), a = !T(e) || e !== this._$AH && e !== M, a && (this._$AH = e);
		else {
			let r = e, o, s;
			for (e = i[0], o = 0; o < i.length - 1; o++) s = I(this, r[n + o], t, o), s === M && (s = this._$AH[o]), a ||= !T(s) || s !== this._$AH[o], s === N ? e = N : e !== N && (e += (s ?? "") + i[o + 1]), this._$AH[o] = s;
		}
		a && !r && this.j(e);
	}
	j(e) {
		e === N ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
	}
}, be = class extends R {
	constructor() {
		super(...arguments), this.type = 3;
	}
	j(e) {
		this.element[this.name] = e === N ? void 0 : e;
	}
}, xe = class extends R {
	constructor() {
		super(...arguments), this.type = 4;
	}
	j(e) {
		this.element.toggleAttribute(this.name, !!e && e !== N);
	}
}, Se = class extends R {
	constructor(e, t, n, r, i) {
		super(e, t, n, r, i), this.type = 5;
	}
	_$AI(e, t = this) {
		if ((e = I(this, e, t, 0) ?? N) === M) return;
		let n = this._$AH, r = e === N && n !== N || e.capture !== n.capture || e.once !== n.once || e.passive !== n.passive, i = e !== N && (n === N || r);
		r && this.element.removeEventListener(this.name, this, n), i && this.element.addEventListener(this.name, this, e), this._$AH = e;
	}
	handleEvent(e) {
		typeof this._$AH == "function" ? this._$AH.call(this.options?.host ?? this.element, e) : this._$AH.handleEvent(e);
	}
}, Ce = class {
	constructor(e, t, n) {
		this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = n;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	_$AI(e) {
		I(this, e);
	}
}, we = {
	M: se,
	P: x,
	A: S,
	C: 1,
	L: ve,
	R: ye,
	D: le,
	V: I,
	I: L,
	H: R,
	N: xe,
	U: Se,
	B: be,
	F: Ce
}, Te = y.litHtmlPolyfillSupport;
Te?.(F, L), (y.litHtmlVersions ??= []).push("3.3.3");
var Ee = (e, t, n) => {
	let r = n?.renderBefore ?? t, i = r._$litPart$;
	if (i === void 0) {
		let e = n?.renderBefore ?? null;
		r._$litPart$ = i = new L(t.insertBefore(w(), e), e, void 0, n ?? {});
	}
	return i._$AI(e), i;
}, z = globalThis, B = class extends v {
	constructor() {
		super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
	}
	createRenderRoot() {
		let e = super.createRenderRoot();
		return this.renderOptions.renderBefore ??= e.firstChild, e;
	}
	update(e) {
		let t = this.render();
		this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = Ee(t, this.renderRoot, this.renderOptions);
	}
	connectedCallback() {
		super.connectedCallback(), this._$Do?.setConnected(!0);
	}
	disconnectedCallback() {
		super.disconnectedCallback(), this._$Do?.setConnected(!1);
	}
	render() {
		return M;
	}
};
B._$litElement$ = !0, B.finalized = !0, z.litElementHydrateSupport?.({ LitElement: B });
var De = z.litElementPolyfillSupport;
De?.({ LitElement: B }), (z.litElementVersions ??= []).push("4.2.2");
//#endregion
//#region frontend/src/localize.ts
var Oe = {
	addPlant: "Add plant",
	addGroup: "Add group",
	create: "Create",
	cancel: "Cancel",
	created: "Added successfully",
	createLoadError: "The setup form could not be loaded. Check that the PlantBased hub is loaded and try again.",
	createError: "Could not add this plant or group. Check the values or try again.",
	groups: "Groups",
	areas: "Areas",
	yourPlants: "Your plants",
	panelHint: "Care, groups and rooms at a glance.",
	settings: "Settings",
	details: "Device details",
	groupDetails: "Group details",
	noArea: "No area",
	noGroup: "No group",
	showPlants: "Show plants",
	view: "View",
	search: "Search",
	searchHint: "Plant, group or area…",
	dueOnly: "Care due only",
	noMatches: "No matching plants",
	noMatchesHint: "Change the search or turn off the care filter.",
	openMenu: "Open sidebar",
	offline: "Disconnected. Care actions are unavailable until Home Assistant reconnects.",
	plants: "Plants",
	overview: "Plant overview",
	total: "Total",
	water: "Watering",
	fertilize: "Fertilizing",
	overdue: "Overdue",
	ok: "Doing well",
	due: "Care due",
	paused: "Paused",
	unavailable: "Unavailable",
	loading: "Loading plants…",
	watered: "Watered",
	fertilized: "Fertilized",
	snooze: "Snooze",
	snoozeWater: "Watering +1 day",
	snoozeFertilizer: "Fertilizing +1 day",
	today: "Due today",
	days: "In {n} days",
	tomorrow: "Tomorrow",
	overdueDays: "{n} days overdue",
	overdueDay: "1 day overdue",
	disabled: "Not enabled",
	noPlants: "No plants yet",
	noPlantsHint: "Add plants in the PlantBased integration settings.",
	allDone: "All caught up",
	allDoneHint: "Your plants have no care due right now.",
	groupEmpty: "This group has no plants yet.",
	chooseDevice: "Choose a plant or group",
	missingDevice: "This plant or group is no longer available.",
	registryError: "Plant information could not be loaded.",
	retry: "Try again",
	actionError: "Care could not be saved. Please try again.",
	saved: "Care saved",
	title: "Title",
	titleHint: "Optional",
	showActions: "Show care buttons",
	plant: "Plant",
	group: "Group",
	cardDescription: "Care for a plant or a group",
	overviewDescription: "Care counts and plants needing attention",
	selected: "Selected device",
	noDevices: "Add a plant or group in the PlantBased integration first.",
	invalidConfig: "Choose a PlantBased plant or group device.",
	invalidTitle: "Enter a text title.",
	invalidActions: "Choose whether care buttons are shown."
}, ke = {
	addPlant: "Pflanze hinzufügen",
	addGroup: "Gruppe hinzufügen",
	create: "Anlegen",
	cancel: "Abbrechen",
	created: "Erfolgreich hinzugefügt",
	createLoadError: "Das Formular konnte nicht geladen werden. Prüfe, ob der PlantBased-Hub geladen ist, und versuche es erneut.",
	createError: "Die Pflanze oder Gruppe konnte nicht angelegt werden. Prüfe die Eingaben oder versuche es erneut.",
	groups: "Gruppen",
	areas: "Bereiche",
	yourPlants: "Deine Pflanzen",
	panelHint: "Pflege, Gruppen und Räume auf einen Blick.",
	settings: "Einstellungen",
	details: "Gerätedetails",
	groupDetails: "Gruppendetails",
	noArea: "Ohne Bereich",
	noGroup: "Keine Gruppe",
	showPlants: "Pflanzen anzeigen",
	view: "Ansicht",
	search: "Suchen",
	searchHint: "Pflanze, Gruppe oder Bereich…",
	dueOnly: "Nur fällige Pflege",
	noMatches: "Keine passenden Pflanzen",
	noMatchesHint: "Ändere die Suche oder deaktiviere den Pflegefilter.",
	openMenu: "Seitenleiste öffnen",
	offline: "Verbindung getrennt. Pflegeaktionen sind nach der Wiederverbindung mit Home Assistant verfügbar.",
	plants: "Pflanzen",
	overview: "Pflanzenübersicht",
	total: "Gesamt",
	water: "Gießen",
	fertilize: "Düngen",
	overdue: "Überfällig",
	ok: "Gut versorgt",
	due: "Pflege fällig",
	paused: "Pausiert",
	unavailable: "Nicht verfügbar",
	loading: "Pflanzen werden geladen…",
	watered: "Gewässert",
	fertilized: "Gedüngt",
	snooze: "Verschieben",
	snoozeWater: "Gießen +1 Tag",
	snoozeFertilizer: "Düngen +1 Tag",
	today: "Heute fällig",
	days: "In {n} Tagen",
	tomorrow: "Morgen",
	overdueDays: "{n} Tage überfällig",
	overdueDay: "1 Tag überfällig",
	disabled: "Nicht aktiviert",
	noPlants: "Noch keine Pflanzen",
	noPlantsHint: "Füge Pflanzen in den Einstellungen der PlantBased-Integration hinzu.",
	allDone: "Alles versorgt",
	allDoneHint: "Für deine Pflanzen ist gerade keine Pflege fällig.",
	groupEmpty: "Diese Gruppe hat noch keine Pflanzen.",
	chooseDevice: "Pflanze oder Gruppe wählen",
	missingDevice: "Diese Pflanze oder Gruppe ist nicht mehr verfügbar.",
	registryError: "Die Pflanzeninformationen konnten nicht geladen werden.",
	retry: "Erneut versuchen",
	actionError: "Die Pflege konnte nicht gespeichert werden. Bitte erneut versuchen.",
	saved: "Pflege gespeichert",
	title: "Titel",
	titleHint: "Optional",
	showActions: "Pflegeaktionen anzeigen",
	plant: "Pflanze",
	group: "Gruppe",
	cardDescription: "Pflege für eine Pflanze oder Gruppe",
	overviewDescription: "Pflegezähler und Pflanzen mit fälliger Pflege",
	selected: "Gewähltes Gerät",
	noDevices: "Füge zuerst eine Pflanze oder Gruppe in der PlantBased-Integration hinzu.",
	invalidConfig: "Wähle ein PlantBased-Pflanzen- oder Gruppengerät.",
	invalidTitle: "Gib einen Titel als Text ein.",
	invalidActions: "Wähle, ob Pflegeaktionen angezeigt werden."
}, Ae = (e) => (e?.locale?.language ?? e?.language ?? "en").toLowerCase().startsWith("de") ? "de" : "en", V = (e, t, n) => (Ae(e) === "de" ? ke : Oe)[t].replace("{n}", String(n ?? ""));
function je(e, t) {
	return t === null ? V(e, "unavailable") : t === 0 ? V(e, "today") : t === 1 ? V(e, "tomorrow") : t === -1 ? V(e, "overdueDay") : V(e, t < 0 ? "overdueDays" : "days", Math.abs(t));
}
//#endregion
//#region frontend/src/model.ts
var Me = [
	"generic",
	"monstera",
	"ficus",
	"pothos",
	"snake_plant",
	"succulent",
	"cactus",
	"fern",
	"orchid",
	"herb",
	"palm",
	"hanging_plant"
];
function H(e) {
	let t = new URL(import.meta.url), n = new URL(`illustrations/${Me.includes(e) ? e : "generic"}.svg`, t);
	return n.search = new URL(import.meta.url).search, n.href;
}
function Ne(e, t) {
	if (typeof e != "string") return H(t);
	try {
		if (e.startsWith("/local/") || e.startsWith("/plantbased/illustrations/")) return new URL(e, location.origin).href;
		let t = new URL(e);
		if (["http:", "https:"].includes(t.protocol) && !t.username && !t.password) return t.href;
	} catch {}
	return H(t);
}
function Pe(e, t = !1, n) {
	if (!e || typeof e != "object" || !t && e.device_id !== void 0 && typeof e.device_id != "string") throw Error(V(n, "invalidConfig"));
	if (e.title !== void 0 && typeof e.title != "string") throw Error(V(n, "invalidTitle"));
	if (e.show_actions !== void 0 && typeof e.show_actions != "boolean") throw Error(V(n, "invalidActions"));
	return { ...e };
}
var U = (e) => e.name_by_user || e.name || "PlantBased";
function W(e) {
	return e.translation_key || e.unique_id.slice((e.config_subentry_id || e.config_entry_id || "").length + 1);
}
function G(e, t, n, r) {
	let i = t.entities.find((e) => e.device_id === n && W(e) === r && !e.disabled_by);
	return i ? e.states[i.entity_id] : void 0;
}
function K(e) {
	if (!e || [
		"unknown",
		"unavailable",
		""
	].includes(e.state)) return null;
	let t = Number(e.state);
	return Number.isFinite(t) ? t : null;
}
function q(e, t) {
	let n = new Map(t.devices.filter((e) => e.model === "Group").map((e) => [t.entities.find((t) => t.device_id === e.id && t.config_subentry_id)?.config_subentry_id ?? e.identifiers.find(([e]) => e === "plantbased")?.[1], U(e)]));
	return t.devices.filter((e) => e.model === "Plant").map((r) => {
		let i = t.entities.filter((e) => e.device_id === r.id), a = G(e, t, r.id, "care_status"), o = a?.attributes ?? {}, s = i.find((e) => e.config_subentry_id)?.config_subentry_id ?? String(o.subentry_id ?? ""), c = !!a && [
			"ok",
			"water",
			"fertilize",
			"water_and_fertilize",
			"paused"
		].includes(a.state) && !r.disabled_by && e.connected !== !1, l = c && ["water", "water_and_fertilize"].includes(a.state), u = c && ["fertilize", "water_and_fertilize"].includes(a.state), d = K(G(e, t, r.id, "days_until_watering")), f = K(G(e, t, r.id, "days_until_fertilizing")), p = c ? a.state : "unavailable", m = c ? p === "paused" ? "paused" : l && d !== null && d < 0 || u && f !== null && f < 0 ? "overdue" : l || u ? "due" : "ok" : "unavailable", h = typeof o.image_preset == "string" ? o.image_preset : "generic";
		return {
			deviceId: r.id,
			subentryId: s,
			name: U(r),
			group: n.get(typeof o.group_id == "string" ? o.group_id : void 0) ?? (typeof o.group == "string" ? o.group : null),
			groupId: typeof o.group_id == "string" ? o.group_id : null,
			areaId: r.area_id ?? null,
			area: t.areas?.find((e) => e.area_id === r.area_id)?.name ?? null,
			image: Ne(o.image_url, h),
			preset: h,
			status: p,
			tone: m,
			available: c,
			waterDue: l,
			fertilizerDue: u,
			waterDays: d,
			fertilizerDays: f,
			fertilizingEnabled: o.fertilizing_enabled !== !1
		};
	}).sort((e, t) => e.name.localeCompare(t.name));
}
function Fe(e, t) {
	return [
		"total_plants",
		"plants_needing_water",
		"plants_needing_fertilizer",
		"plants_overdue"
	].map((n) => {
		let r = t.entities.find((e) => !e.config_subentry_id && W(e) === n && !e.disabled_by);
		return e.connected === !1 ? null : K(r ? e.states[r.entity_id] : void 0);
	});
}
//#endregion
//#region frontend/src/registry.ts
var Ie = class {
	constructor(e, t = !1) {
		this.host = e, this.includeAreas = t, this.error = !1, this.connected = !1, this.generation = 0, this.unsubs = [], this.loading = !1, this.dirty = !1, this.onReady = () => {
			this.refresh();
		}, e.addController(this);
	}
	hostConnected() {
		this.connected = !0, this.attach();
	}
	hostDisconnected() {
		this.connected = !1, this.detach();
	}
	setHass(e) {
		this.hass = e, e?.connection !== this.connection && (this.detach(), this.data = void 0, this.error = !1, this.attach());
	}
	attach() {
		if (!this.connected || !this.hass || this.connection) return;
		let e = this.connection = this.hass.connection, t = this.generation;
		e.addEventListener("ready", this.onReady);
		for (let n of [
			"entity_registry_updated",
			"device_registry_updated",
			...this.includeAreas ? ["area_registry_updated"] : []
		]) e.subscribeEvents(this.onReady, n).then((e) => {
			t === this.generation ? this.unsubs.push(e) : e();
		}).catch(() => {
			t === this.generation && (this.error = !0, this.host.requestUpdate());
		});
		this.refresh();
	}
	detach() {
		this.generation++, this.connection?.removeEventListener("ready", this.onReady), this.connection = void 0, this.unsubs.splice(0).forEach((e) => e()), this.loading = !1, this.dirty = !1;
	}
	async refresh() {
		if (!this.hass || !this.connected) return;
		if (this.loading) {
			this.dirty = !0;
			return;
		}
		let e = this.generation;
		this.loading = !0;
		try {
			let [t, n, r] = await Promise.all([
				this.hass.callWS({ type: "config/entity_registry/list" }),
				this.hass.callWS({ type: "config/device_registry/list" }),
				this.includeAreas ? this.hass.callWS({ type: "config/area_registry/list" }) : Promise.resolve([])
			]);
			if (e !== this.generation) return;
			this.data = {
				areas: r,
				entities: t.filter((e) => e.platform === "plantbased"),
				devices: n.filter((e) => e.identifiers.some(([e]) => e === "plantbased"))
			}, this.error = !1;
		} catch {
			e === this.generation && (this.error = !0);
		} finally {
			e === this.generation && (this.loading = !1, this.host.requestUpdate(), this.dirty && (this.dirty = !1, this.refresh()));
		}
	}
}, J = o`
  :host {
    container-type: inline-size;
    display: block;
    color: var(--primary-text-color, #263b31);
    font-family: var(--paper-font-body1_-_font-family, inherit);
    --pb-green: var(--success-color, #397656);
    --pb-line: var(--divider-color, #dfe6df);
    --pb-muted: var(--secondary-text-color, #66756c);
    --pb-surface: var(--card-background-color, #fff);
  }
  * {
    box-sizing: border-box;
  }
  ha-card {
    display: block;
    overflow: hidden;
    border-radius: var(--ha-card-border-radius, 18px);
    background: var(--ha-card-background, var(--pb-surface));
    border: var(--ha-card-border-width, 1px) solid
      var(--ha-card-border-color, var(--pb-line));
    box-shadow: var(--ha-card-box-shadow, none);
  }
  .header {
    padding: 22px 22px 14px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 7px;
    color: var(--pb-muted);
    font-size: 11px;
    font-weight: 650;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
  .brand::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--pb-green);
  }
  h2 {
    font-size: 23px;
    line-height: 1.25;
    font-weight: 550;
    margin: 9px 0 0;
    letter-spacing: -0.025em;
    overflow-wrap: anywhere;
  }
  h3 {
    font-size: 18px;
    line-height: 1.3;
    font-weight: 600;
    margin: 0;
    overflow-wrap: anywhere;
  }
  p {
    margin: 8px 0 0;
    line-height: 1.5;
    color: var(--pb-muted);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr));
    gap: 12px;
    padding: 0 14px 14px;
  }
  .single {
    padding: 0 8px 8px;
  }
  .plant {
    padding: 16px;
    min-width: 0;
    border: 1px solid var(--pb-line);
    border-radius: 14px;
    background: var(--pb-surface);
  }
  .single .plant {
    border: 0;
    padding: 8px 14px 14px;
  }
  .plant-top {
    display: grid;
    grid-template-columns: 78px minmax(0, 1fr);
    align-items: center;
    gap: 16px;
  }
  .illustration {
    width: 78px;
    height: 94px;
    object-fit: contain;
    border-radius: 14px;
    background: color-mix(in srgb, var(--pb-green) 7%, var(--pb-surface));
  }
  .plant-group {
    font-size: 12px;
    margin: 4px 0 8px;
    overflow-wrap: anywhere;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 20px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
    line-height: 1.3;
    background: color-mix(in srgb, var(--pb-green) 10%, var(--pb-surface));
    color: var(--pb-green);
  }
  .badge.due {
    color: var(--warning-color, #a66413);
    background: color-mix(
      in srgb,
      var(--warning-color, #a66413) 12%,
      var(--pb-surface)
    );
  }
  .badge.overdue {
    color: var(--error-color, #b94c42);
    background: color-mix(
      in srgb,
      var(--error-color, #b94c42) 10%,
      var(--pb-surface)
    );
  }
  .badge.paused,
  .badge.unavailable {
    color: var(--pb-muted);
    background: var(--secondary-background-color, #f0f2ef);
  }
  .chips {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 14px 0;
  }
  .chip {
    min-width: 0;
    padding: 9px 10px;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
  }
  .chip-label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--pb-muted);
  }
  .chip-value {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    font-weight: 550;
    overflow-wrap: anywhere;
  }
  .chip.active {
    border-color: color-mix(
      in srgb,
      var(--warning-color, #a66413) 40%,
      var(--pb-line)
    );
  }
  .actions {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 6px;
  }
  button,
  summary {
    font: inherit;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }
  button {
    min-height: 44px;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
    padding: 8px 10px;
    background: var(--pb-surface);
    color: var(--primary-text-color, #263b31);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 12px;
  }
  button:hover,
  summary:hover {
    background: var(--secondary-background-color, #f0f2ef);
  }
  button.primary {
    color: var(--pb-green);
    background: color-mix(in srgb, var(--pb-green) 7%, var(--pb-surface));
    border-color: color-mix(in srgb, var(--pb-green) 25%, var(--pb-line));
  }
  button:disabled {
    cursor: default;
    opacity: 0.45;
  }
  button:focus-visible,
  summary:focus-visible,
  input:focus-visible,
  select:focus-visible {
    outline: 2px solid var(--primary-color, #397656);
    outline-offset: 3px;
  }
  details {
    position: relative;
  }
  summary {
    list-style: none;
    min-height: 44px;
    min-width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
    color: var(--pb-muted);
  }
  summary::-webkit-details-marker {
    display: none;
  }
  .snooze-menu {
    display: flex;
    flex-direction: column;
    gap: 5px;
    padding-top: 6px;
    min-width: 140px;
  }
  details[open] {
    flex-basis: 100%;
  }
  details[open] summary {
    max-width: 44px;
  }
  .counts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    padding: 0 22px 20px;
  }
  .count {
    padding: 13px 10px;
    border-radius: 12px;
    background: var(--secondary-background-color, #f2f5f1);
    min-width: 0;
  }
  .count strong {
    display: block;
    margin-top: 7px;
    font-size: 28px;
    font-weight: 550;
    line-height: 1.1;
  }
  .count span {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--pb-muted);
    overflow-wrap: anywhere;
  }
  .count.water {
    background: color-mix(
      in srgb,
      var(--info-color, #3a7c97) 9%,
      var(--pb-surface)
    );
  }
  .count.fertilize {
    background: color-mix(in srgb, var(--pb-green) 9%, var(--pb-surface));
  }
  .count.overdue {
    background: color-mix(
      in srgb,
      var(--error-color, #b94c42) 8%,
      var(--pb-surface)
    );
  }
  .overview-list {
    border-top: 1px solid var(--pb-line);
    padding: 14px;
    display: grid;
    gap: 10px;
  }
  .empty {
    padding: 24px 22px 32px;
    text-align: center;
  }
  .empty img {
    display: block;
    width: 100px;
    height: 114px;
    object-fit: contain;
    margin: 0 auto 14px;
  }
  .empty h3 {
    font-size: 17px;
  }
  .empty p {
    font-size: 13px;
  }
  .feedback {
    padding: 0 22px 12px;
    font-size: 12px;
  }
  .feedback:empty {
    display: none;
  }
  .error {
    color: var(--error-color, #b94c42);
  }
  svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }
  label {
    display: block;
    font-size: 13px;
    margin: 16px 0 6px;
  }
  input[type="text"],
  select {
    display: block;
    width: 100%;
    min-height: 46px;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
    padding: 10px;
    font: inherit;
    color: inherit;
    background: var(--pb-surface);
  }
  .check {
    display: flex;
    gap: 10px;
    align-items: center;
    min-height: 44px;
  }
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: var(--pb-green);
  }
  .editor {
    padding: 4px 0 12px;
  }
  @container (min-width:500px) {
    .counts {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
  @media (prefers-reduced-motion: no-preference) {
    button,
    summary {
      transition: background 0.12s;
    }
  }
`, Y = (e) => A`<svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    ${e === "water" ? j`<path d="M12 3C9 7 5 11 5 15a7 7 0 0 0 14 0c0-4-4-8-7-12Z"/><path d="M8 15a4 4 0 0 0 4 4"/>` : e === "leaf" ? j`<path d="M5 20 17 8M5 16C2 6 12 3 21 3c0 9-3 19-13 16"/>` : e === "clock" ? j`<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>` : j`<path d="M7 15h10l-1 6H8l-1-6ZM12 15V6M12 11C4 12 4 5 4 4c6-1 8 3 8 7ZM12 9c0-5 4-6 8-6 0 5-3 8-8 6Z"/>`}
  </svg>`, X = class extends B {
	constructor(...e) {
		super(...e), this._message = "", this._error = !1, this.pending = /* @__PURE__ */ new Set(), this.registry = new Ie(this, this.includeAreas);
	}
	static {
		this.properties = {
			hass: { attribute: !1 },
			_config: { state: !0 },
			_message: { state: !0 },
			_error: { state: !0 }
		};
	}
	static {
		this.styles = J;
	}
	get includeAreas() {
		return !1;
	}
	setConfig(e) {
		this._config = Pe(e, this.overview, this.hass);
	}
	willUpdate(e) {
		e.has("hass") && this.registry.setHass(this.hass);
	}
	getCardSize() {
		return this.overview ? 5 : 4;
	}
	getGridOptions() {
		return {
			columns: 12,
			min_columns: 6,
			min_rows: 3
		};
	}
	renderStatus() {
		return this.registry.error ? A`<div class="empty" role="alert">
        <p>${V(this.hass, "registryError")}</p>
        <button @click=${() => this.registry.refresh()}>
          ${V(this.hass, "retry")}
        </button>
      </div>` : !this.hass || !this.registry.data ? A`<div class="empty" role="status">
        ${V(this.hass, "loading")}
      </div>` : N;
	}
	feedback() {
		return A`<div
      class="feedback ${this._error ? "error" : ""}"
      role=${this._error ? "alert" : "status"}
      aria-live="polite"
    >
      ${this._message}
    </div>`;
	}
	async act(e, t, n) {
		if (this.hass && e.available && !this.pending.has(e.deviceId)) {
			this.pending.add(e.deviceId), this._message = "", this.requestUpdate();
			try {
				await this.hass.callService("plantbased", t, n ? {
					care_type: n,
					days: 1
				} : {}, { device_id: e.deviceId }, !1), this._message = V(this.hass, "saved"), this._error = !1;
			} catch {
				this._message = V(this.hass, "actionError"), this._error = !0;
			} finally {
				this.pending.delete(e.deviceId), this.requestUpdate();
			}
		}
	}
	plantLinks(e) {
		return N;
	}
	row(e) {
		let t = this.pending.has(e.deviceId) || !e.available, n = e.tone === "paused";
		return A`<article
      class="plant"
      data-device=${e.deviceId}
      aria-label=${e.name}
    >
      <div class="plant-top">
        <img
          class="illustration"
          src=${e.image}
          alt=""
          loading="lazy"
          referrerpolicy="no-referrer"
          @error=${(t) => {
			let n = t.currentTarget, r = H(e.preset);
			n.src !== r && (n.src = r);
		}}
        />
        <div>
          <h3>${e.name}</h3>
          ${e.group ? A`<p class="plant-group">${e.group}</p>` : N}<span
            class="badge ${e.tone}"
            >${V(this.hass, e.tone)}</span
          >
        </div>
      </div>
      <div class="chips">
        <div class="chip ${e.waterDue && !n ? "active" : ""}">
          <span class="chip-label"
            >${Y("water")}${V(this.hass, "water")}</span
          ><span class="chip-value"
            >${je(this.hass, e.available ? e.waterDays : null)}</span
          >
        </div>
        <div class="chip ${e.fertilizerDue && !n ? "active" : ""}">
          <span class="chip-label"
            >${Y("leaf")}${V(this.hass, "fertilize")}</span
          ><span class="chip-value"
            >${e.fertilizingEnabled ? je(this.hass, e.available ? e.fertilizerDays : null) : V(this.hass, "disabled")}</span
          >
        </div>
      </div>
      ${this._config?.show_actions === !1 ? N : A`<div class="actions">
              <button
                class="primary"
                ?disabled=${t}
                @click=${() => this.act(e, "mark_watered")}
              >
                ${Y("water")}${V(this.hass, "watered")}
              </button>
              <button
                ?disabled=${t || !e.fertilizingEnabled}
                @click=${() => this.act(e, "mark_fertilized")}
              >
                ${Y("leaf")}${V(this.hass, "fertilized")}
              </button>
              ${t ? A`<button disabled aria-label=${V(this.hass, "snooze")}>
                      ${Y("clock")}
                    </button>` : A`<details>
                      <summary
                        aria-label=${V(this.hass, "snooze")}
                        title=${V(this.hass, "snooze")}
                      >
                        ${Y("clock")}
                      </summary>
                      <div class="snooze-menu">
                        <button
                          @click=${() => this.act(e, "snooze", "water")}
                        >
                          ${V(this.hass, "snoozeWater")}</button
                        >${e.fertilizingEnabled ? A`<button @click=${() => this.act(e, "snooze", "fertilize")}>${V(this.hass, "snoozeFertilizer")}</button>` : N}
                      </div>
                    </details>`}
            </div>`}
      ${this.plantLinks(e)}
    </article>`;
	}
	empty(e, t) {
		return A`<div class="empty">
      <img src=${H("generic")} alt="" />
      <h3>${V(this.hass, e)}</h3>
      <p>${V(this.hass, t)}</p>
    </div>`;
	}
}, Le = class extends X {
	constructor(...e) {
		super(...e), this.overview = !1;
	}
	static getConfigElement() {
		return document.createElement("plantbased-card-editor");
	}
	static getStubConfig(e) {
		return {
			device_id: Object.values(e?.devices ?? {}).find((e) => ["Plant", "Group"].includes(e.model ?? "") && e.identifiers.some(([e]) => e === "plantbased"))?.id ?? "",
			show_actions: !0
		};
	}
	render() {
		if (!this.hass || !this.registry.data || this.registry.error) return A`<ha-card>${this.renderStatus()}</ha-card>`;
		let e = this.registry.data, t = e.devices.find((e) => e.id === this._config?.device_id && ["Plant", "Group"].includes(e.model ?? ""));
		if (!t) return A`<ha-card
        >${this.empty(this._config?.device_id ? "missingDevice" : "chooseDevice", "noDevices")}</ha-card
      >`;
		let n = t.model === "Group", r = e.entities.find((e) => e.device_id === t.id && e.config_subentry_id)?.config_subentry_id, i = q(this.hass, e).filter((e) => n ? e.groupId === r : e.deviceId === t.id);
		return A`<ha-card
      ><header class="header">
        <div class="brand">PlantBased</div>
        ${this._config?.title || n ? A`<h2>${this._config?.title || U(t)}</h2>` : N}${n ? A`<p>${i.length} ${V(this.hass, i.length === 1 ? "plant" : "plants")}</p>` : N}
      </header>
      ${i.length ? A`<div class=${n ? "grid" : "single"}>${i.map((e) => this.row(e))}</div>` : A`<div class="empty"><p>${V(this.hass, "groupEmpty")}</p></div>`}${this.feedback()}</ha-card
    >`;
	}
}, Re = class extends X {
	constructor(...e) {
		super(...e), this.overview = !0;
	}
	static getConfigElement() {
		return document.createElement("plantbased-overview-card-editor");
	}
	static getStubConfig() {
		return { show_actions: !0 };
	}
	render() {
		if (!this.hass || !this.registry.data || this.registry.error) return A`<ha-card>${this.renderStatus()}</ha-card>`;
		let e = q(this.hass, this.registry.data), t = e.filter((e) => e.waterDue || e.fertilizerDue).sort((e, t) => Number(t.tone === "overdue") - Number(e.tone === "overdue") || e.name.localeCompare(t.name)), n = Fe(this.hass, this.registry.data), r = [
			"total",
			"water",
			"fertilize",
			"overdue"
		], i = [
			"plants",
			"water",
			"leaf",
			"clock"
		], a = this.registry.data.entities.some((e) => !e.config_subentry_id && W(e) === "total_plants");
		return A`<ha-card
      ><header class="header">
        <div class="brand">PlantBased</div>
        <h2>${this._config?.title || V(this.hass, "overview")}</h2>
      </header>
      <div class="counts">
        ${r.map((e, t) => A`<div class="count ${e}" aria-label=${V(this.hass, e)}><span>${Y(i[t])}${V(this.hass, e)}</span><strong>${n[t] ?? "—"}</strong></div>`)}
      </div>
      ${e.length ? !a || n.some((e) => e === null) ? A`<div class="empty"><p>${V(this.hass, "unavailable")}</p></div>` : t.length ? A`<div class="overview-list">${t.map((e) => this.row(e))}</div>` : this.empty("allDone", "allDoneHint") : this.empty("noPlants", "noPlantsHint")}${this.feedback()}</ha-card
    >`;
	}
}, ze = class extends B {
	constructor(...e) {
		super(...e), this._config = { type: "custom:plantbased-card" }, this.overview = !1, this.registry = new Ie(this);
	}
	static {
		this.properties = {
			hass: { attribute: !1 },
			_config: { state: !0 }
		};
	}
	static {
		this.styles = J;
	}
	setConfig(e) {
		this._config = { ...e };
	}
	willUpdate(e) {
		e.has("hass") && this.registry.setHass(this.hass);
	}
	change(e, t) {
		let n = {
			...this._config,
			[e]: t
		};
		e === "title" && !t && delete n.title, this._config = n, this.dispatchEvent(new CustomEvent("config-changed", {
			detail: { config: n },
			bubbles: !0,
			composed: !0
		}));
	}
	render() {
		let e = this.registry.data?.devices.filter((e) => ["Plant", "Group"].includes(e.model ?? "")).sort((e, t) => U(e).localeCompare(U(t))) ?? [], t = this._config.device_id && !e.some((e) => e.id === this._config.device_id);
		return A`<div class="editor">
      ${this.overview ? N : A`<label for="device">${V(this.hass, "chooseDevice")}</label
              ><select
                id="device"
                .value=${this._config.device_id || ""}
                @change=${(e) => this.change("device_id", e.currentTarget.value)}
              >
                <option value="">${V(this.hass, "chooseDevice")}</option>
                ${t ? A`<option value=${this._config.device_id}>${V(this.hass, "unavailable")}</option>` : N}${e.map((e) => A`<option value=${e.id}>${U(e)} · ${V(this.hass, e.model === "Plant" ? "plant" : "group")}</option>`)}</select
              >${e.length ? N : A`<p>${V(this.hass, this.registry.data ? "noDevices" : "loading")}</p>`}${this.registry.error ? A`<p role="alert">${V(this.hass, "registryError")}</p>
                      <button @click=${() => this.registry.refresh()}>
                        ${V(this.hass, "retry")}
                      </button>` : N}`} <label for="title">${V(this.hass, "title")}</label
      ><input
        id="title"
        type="text"
        placeholder=${V(this.hass, "titleHint")}
        .value=${this._config.title ?? ""}
        @input=${(e) => this.change("title", e.currentTarget.value)}
      />
      <label class="check"
        ><input
          type="checkbox"
          .checked=${this._config.show_actions !== !1}
          @change=${(e) => this.change("show_actions", e.currentTarget.checked)}
        />${V(this.hass, "showActions")}</label
      >
    </div>`;
	}
}, Be = class extends ze {
	constructor(...e) {
		super(...e), this.overview = !0;
	}
}, Ve = {
	ATTRIBUTE: 1,
	CHILD: 2,
	PROPERTY: 3,
	BOOLEAN_ATTRIBUTE: 4,
	EVENT: 5,
	ELEMENT: 6
}, He = (e) => (...t) => ({
	_$litDirective$: e,
	values: t
}), Ue = class {
	constructor(e) {}
	get _$AU() {
		return this._$AM._$AU;
	}
	_$AT(e, t, n) {
		this._$Ct = e, this._$AM = t, this._$Ci = n;
	}
	_$AS(e, t) {
		return this.update(e, t);
	}
	update(e, t) {
		return this.render(...t);
	}
}, { I: We } = we, Ge = (e) => e, Ke = () => document.createComment(""), Z = (e, t, n) => {
	let r = e._$AA.parentNode, i = t === void 0 ? e._$AB : t._$AA;
	if (n === void 0) n = new We(r.insertBefore(Ke(), i), r.insertBefore(Ke(), i), e, e.options);
	else {
		let t = n._$AB.nextSibling, a = n._$AM, o = a !== e;
		if (o) {
			let t;
			n._$AQ?.(e), n._$AM = e, n._$AP !== void 0 && (t = e._$AU) !== a._$AU && n._$AP(t);
		}
		if (t !== i || o) {
			let e = n._$AA;
			for (; e !== t;) {
				let t = Ge(e).nextSibling;
				Ge(r).insertBefore(e, i), e = t;
			}
		}
	}
	return n;
}, Q = (e, t, n = e) => (e._$AI(t, n), e), qe = {}, Je = (e, t = qe) => e._$AH = t, Ye = (e) => e._$AH, Xe = (e) => {
	e._$AR(), e._$AA.remove();
}, Ze = (e, t, n) => {
	let r = /* @__PURE__ */ new Map();
	for (let i = t; i <= n; i++) r.set(e[i], i);
	return r;
}, $ = He(class extends Ue {
	constructor(e) {
		if (super(e), e.type !== Ve.CHILD) throw Error("repeat() can only be used in text expressions");
	}
	dt(e, t, n) {
		let r;
		n === void 0 ? n = t : t !== void 0 && (r = t);
		let i = [], a = [], o = 0;
		for (let t of e) i[o] = r ? r(t, o) : o, a[o] = n(t, o), o++;
		return {
			values: a,
			keys: i
		};
	}
	render(e, t, n) {
		return this.dt(e, t, n).values;
	}
	update(e, [t, n, r]) {
		let i = Ye(e), { values: a, keys: o } = this.dt(t, n, r);
		if (!Array.isArray(i)) return this.ut = o, a;
		let s = this.ut ??= [], c = [], l, u, d = 0, f = i.length - 1, p = 0, m = a.length - 1;
		for (; d <= f && p <= m;) if (i[d] === null) d++;
		else if (i[f] === null) f--;
		else if (s[d] === o[p]) c[p] = Q(i[d], a[p]), d++, p++;
		else if (s[f] === o[m]) c[m] = Q(i[f], a[m]), f--, m--;
		else if (s[d] === o[m]) c[m] = Q(i[d], a[m]), Z(e, c[m + 1], i[d]), d++, m--;
		else if (s[f] === o[p]) c[p] = Q(i[f], a[p]), Z(e, i[d], i[f]), f--, p++;
		else if (l === void 0 && (l = Ze(o, p, m), u = Ze(s, d, f)), l.has(s[d])) {
			if (l.has(s[f])) {
				let t = u.get(o[p]), n = t === void 0 ? null : i[t];
				if (n === null) {
					let t = Z(e, i[d]);
					Q(t, a[p]), c[p] = t;
				} else c[p] = Q(n, a[p]), Z(e, i[d], n), i[t] = null;
				p++;
			} else Xe(i[f]), f--;
		} else Xe(i[d]), d++;
		for (; p <= m;) {
			let t = Z(e, c[m + 1]);
			Q(t, a[p]), c[p++] = t;
		}
		for (; d <= f;) {
			let e = i[d++];
			e !== null && Xe(e);
		}
		return this.ut = o, Je(e, c), M;
	}
}), Qe = class extends X {
	constructor(...e) {
		super(...e), this.overview = !0, this.narrow = !1, this._view = "plants", this._search = "", this._dueOnly = !1;
	}
	static {
		this.properties = {
			...X.properties,
			narrow: { type: Boolean },
			_view: { state: !0 },
			_search: { state: !0 },
			_dueOnly: { state: !0 },
			_creation: { state: !0 }
		};
	}
	get includeAreas() {
		return !0;
	}
	image(e) {
		return A`<img
      src=${e?.image ?? H("generic")}
      alt=""
      loading="lazy"
      referrerpolicy="no-referrer"
      @error=${(t) => {
			let n = t.currentTarget, r = H(e?.preset ?? "generic");
			n.src !== r && (n.src = r);
		}}
    />`;
	}
	plantLinks(e) {
		return A`<footer class="plant-footer">
      <span>${e.area ?? V(this.hass, "noArea")}</span>
      ${this.hass?.user?.is_admin ? A`<a href=${`/config/devices/device/${encodeURIComponent(e.deviceId)}`}>${V(this.hass, "details")}</a>` : N}
    </footer>`;
	}
	counts(e) {
		let t = [
			e.length,
			e.filter((e) => e.waterDue).length,
			e.filter((e) => e.fertilizerDue).length,
			e.filter((e) => e.tone === "overdue").length
		], n = [
			"total",
			"water",
			"fertilize",
			"overdue"
		], r = [
			"plants",
			"water",
			"leaf",
			"clock"
		];
		return A`<div class="counts">
      ${n.map((e, n) => A`<div class="count ${e}"><span>${Y(r[n])}${V(this.hass, e)}</span><strong>${t[n]}</strong></div>`)}
    </div>`;
	}
	plantMatches(e) {
		let t = this._search.trim().toLocaleLowerCase();
		return (!this._dueOnly || e.waterDue || e.fertilizerDue) && (!t || [
			e.name,
			e.group,
			e.area
		].some((e) => e?.toLocaleLowerCase().includes(t)));
	}
	collections(e) {
		let t = this.registry.data;
		if (this._view === "areas") {
			let t = /* @__PURE__ */ new Map();
			for (let n of e) {
				let e = n.areaId ?? "";
				t.has(e) || t.set(e, {
					id: e,
					name: n.area ?? V(this.hass, "noArea"),
					members: []
				}), t.get(e).members.push(n);
			}
			return [...t.values()].sort((e, t) => e.name.localeCompare(t.name));
		}
		let n = t.devices.filter((e) => e.model === "Group").map((n) => {
			let r = t.entities.find((e) => e.device_id === n.id && e.config_subentry_id)?.config_subentry_id ?? n.identifiers.find(([e]) => e === "plantbased")?.[1] ?? n.id;
			return {
				id: r,
				deviceId: n.id,
				name: U(n),
				members: e.filter((e) => e.groupId === r)
			};
		}), r = e.filter((e) => !n.some((t) => t.id === e.groupId)), i = n;
		return r.length && i.push({
			id: "unassigned",
			name: V(this.hass, "noGroup"),
			members: r
		}), i.sort((e, t) => e.name.localeCompare(t.name));
	}
	visibleCollections(e) {
		let t = this._search.trim().toLocaleLowerCase();
		return this.collections(e).map((e) => {
			let n = e.name.toLocaleLowerCase().includes(t), r = e.members.filter((e) => n ? !this._dueOnly || e.waterDue || e.fertilizerDue : this.plantMatches(e));
			return {
				collection: e,
				shown: r,
				visible: r.length > 0 || !e.members.length && n && !this._dueOnly
			};
		}).filter((e) => e.visible);
	}
	collection(e, t) {
		if (this._view === "areas") return A`<section class="area-section" aria-label=${e.name}>
        <div class="section-title">
          <h2>${e.name}</h2>
          <span
            >${t.length}
            ${V(this.hass, t.length === 1 ? "plant" : "plants")}</span
          >
        </div>
        <div class="plant-grid">
          ${$(t, (e) => e.deviceId, (e) => this.row(e))}
        </div>
      </section>`;
		let n = [
			"overdue",
			"due",
			"unavailable",
			"paused",
			"ok"
		].find((t) => e.members.some((e) => e.tone === t)) ?? "ok";
		return A`<article class="collection-card" aria-label=${e.name}>
      <div class="collection-heading">
        <div class="collection-images">
          ${(e.members.length ? e.members.slice(0, 3) : [void 0]).map((e) => this.image(e))}
        </div>
        <div>
          <h2>${e.name}</h2>
          <p>
            ${e.members.length}
            ${V(this.hass, e.members.length === 1 ? "plant" : "plants")}
          </p>
          ${e.members.length ? A`<span class="badge ${n}">${V(this.hass, n)}</span>` : N}
        </div>
      </div>
      ${this.counts(e.members)}
      ${t.length ? A`<details class="members">
              <summary>${V(this.hass, "showPlants")} · ${t.length}</summary>
              <div class="member-grid">
                ${$(t, (e) => e.deviceId, (e) => this.row(e))}
              </div>
            </details>` : A`<p class="group-empty">${V(this.hass, "groupEmpty")}</p>`}
      ${e.deviceId && this.hass?.user?.is_admin ? A`<a class="collection-link" href=${`/config/devices/device/${encodeURIComponent(e.deviceId)}`}>${V(this.hass, "groupDetails")}</a>` : N}
    </article>`;
	}
	render() {
		let e = this.hass && this.registry.data ? q(this.hass, this.registry.data) : [], t = e.filter((e) => this.plantMatches(e)), n = this.registry.data ? this.visibleCollections(e) : [];
		return A`<div class="toolbar">
        <button
          class="menu"
          aria-label=${V(this.hass, "openMenu")}
          @click=${() => this.dispatchEvent(new CustomEvent("hass-toggle-menu", {
			bubbles: !0,
			composed: !0
		}))}
        >
          ☰
        </button>
        <span class="toolbar-brand">${Y("plants")} PlantBased</span>
        ${this.hass?.user?.is_admin ? A`<a class="settings" href="/config/integrations/integration/plantbased">${V(this.hass, "settings")}</a>` : N}
      </div>
      <main>
        <header class="page-heading">
          <div class="brand">PlantBased</div>
          <h1>${V(this.hass, "yourPlants")}</h1>
          <p>${V(this.hass, "panelHint")}</p>
          ${this.hass?.user?.is_admin ? A`<div class="create-actions">
                  <button
                    class="primary"
                    ?disabled=${this.hass.connected === !1 || !!this._creation}
                    @click=${() => {
			this._creation = "plant";
		}}
                  >
                    <span aria-hidden="true">＋</span>
                    ${V(this.hass, "addPlant")}</button
                  ><button
                    ?disabled=${this.hass.connected === !1 || !!this._creation}
                    @click=${() => {
			this._creation = "group";
		}}
                  >
                    <span aria-hidden="true">＋</span>
                    ${V(this.hass, "addGroup")}
                  </button>
                </div>` : N}
        </header>
        ${this.renderStatus()}
        ${this.hass && this.registry.data && !this.registry.error ? A`
                ${this.counts(e)}
                <div class="controls">
                  <nav aria-label=${V(this.hass, "view")}>
                    ${[
			"plants",
			"groups",
			"areas"
		].map((e) => A`<button
                          aria-pressed=${this._view === e}
                          @click=${() => {
			this._view = e;
		}}
                        >
                          ${V(this.hass, e)}
                        </button>`)}
                  </nav>
                  <label class="search"
                    ><span>${V(this.hass, "search")}</span
                    ><input
                      type="search"
                      .value=${this._search}
                      placeholder=${V(this.hass, "searchHint")}
                      @input=${(e) => {
			this._search = e.target.value;
		}}
                  /></label>
                  <label class="due-filter"
                    ><input
                      type="checkbox"
                      .checked=${this._dueOnly}
                      @change=${(e) => {
			this._dueOnly = e.target.checked;
		}}
                    />${V(this.hass, "dueOnly")}</label
                  >
                </div>
                ${!e.length && (this._view !== "groups" || !this.registry.data.devices.some((e) => e.model === "Group")) ? this.empty("noPlants", "noPlantsHint") : this._view === "plants" ? t.length ? A`<div class="plant-grid">
                            ${$(t, (e) => e.deviceId, (e) => this.row(e))}
                          </div>` : this.empty("noMatches", "noMatchesHint") : A`<div
                            class=${this._view === "groups" ? "collection-grid" : "area-list"}
                          >
                            ${$(n, ({ collection: e }) => `${this._view}:${e.id}`, ({ collection: e, shown: t }) => this.collection(e, t))}
                          </div>
                          ${n.length ? N : this.empty("noMatches", "noMatchesHint")}`}
                ${this.hass.connected === !1 ? A`<p role="status" class="offline">${V(this.hass, "offline")}</p>` : N}
                ${this.feedback()}
              ` : N}
      </main>
      ${this._creation ? A`<plantbased-create-dialog
              .hass=${this.hass}
              .kind=${this._creation}
              .areas=${this.registry.data?.areas ?? []}
              @closed=${() => {
			this._creation = void 0;
		}}
              @created=${() => {
			this._creation = void 0, this._error = !1, this._message = V(this.hass, "created"), this.registry.refresh();
		}}
            ></plantbased-create-dialog>` : N}`;
	}
	static {
		this.styles = [J, o`
      :host {
        min-height: 100%;
        background: var(--primary-background-color, #f6f8f4);
      }
      .toolbar {
        min-height: 64px;
        padding: 8px 24px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 1px solid var(--pb-line);
        background: var(--app-header-background-color, var(--pb-surface));
        color: var(--app-header-text-color, var(--primary-text-color));
      }
      .toolbar-brand {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        font-weight: 600;
      }
      .toolbar-brand svg {
        width: 24px;
        height: 24px;
        color: var(--pb-green);
      }
      .menu {
        width: 44px;
        border: 0;
        font-size: 22px;
        color: inherit;
        background: transparent;
      }
      a {
        color: var(--primary-color, #397656);
        text-underline-offset: 3px;
        font-size: 13px;
        min-height: 44px;
        display: inline-flex;
        align-items: center;
      }
      a:focus-visible {
        outline: 2px solid var(--primary-color, #397656);
        outline-offset: 3px;
      }
      .settings {
        margin-left: auto;
        font-weight: 600;
      }
      main {
        max-width: 1360px;
        margin: 0 auto;
        padding: 36px 32px 48px;
      }
      .page-heading {
        margin-bottom: 26px;
      }
      .create-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 20px;
      }
      h1 {
        font-size: clamp(28px, 4vw, 38px);
        font-weight: 550;
        letter-spacing: -0.04em;
        margin: 10px 0 0;
      }
      .page-heading p {
        margin-top: 10px;
      }
      .counts {
        padding: 0;
        gap: 12px;
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }
      .count {
        background: var(--pb-surface);
        border: 1px solid var(--pb-line);
        padding: 16px;
      }
      .count strong {
        font-size: 30px;
      }
      .controls {
        display: flex;
        flex-wrap: wrap;
        align-items: end;
        gap: 16px;
        margin: 28px 0 22px;
      }
      nav {
        display: inline-flex;
        padding: 4px;
        gap: 3px;
        border: 1px solid var(--pb-line);
        border-radius: 13px;
        background: var(--pb-surface);
      }
      nav button {
        border: 0;
        padding: 8px 18px;
        font-size: 13px;
      }
      nav button[aria-pressed="true"] {
        background: color-mix(in srgb, var(--pb-green) 12%, var(--pb-surface));
        color: var(--pb-green);
        font-weight: 600;
      }
      label {
        margin: 0;
      }
      .search {
        flex: 1;
        min-width: 180px;
      }
      .search span {
        display: block;
        font-size: 11px;
        color: var(--pb-muted);
        margin: 0 0 6px 2px;
      }
      input[type="search"] {
        width: 100%;
        min-height: 46px;
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid var(--pb-line);
        background: var(--pb-surface);
        font: inherit;
        color: inherit;
        font-size: 13px;
      }
      .due-filter {
        display: flex;
        align-items: center;
        gap: 8px;
        min-height: 46px;
        cursor: pointer;
      }
      .plant-grid,
      .member-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
        gap: 16px;
      }
      .plant {
        padding: 20px;
      }
      .plant-top {
        grid-template-columns: 94px minmax(0, 1fr);
        gap: 16px;
      }
      .illustration {
        width: 94px;
        height: 112px;
      }
      .plant-footer {
        border-top: 1px solid var(--pb-line);
        margin-top: 14px;
        padding-top: 4px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .plant-footer span {
        color: var(--pb-muted);
        font-size: 12px;
        overflow-wrap: anywhere;
      }
      .collection-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr));
        gap: 18px;
        align-items: start;
      }
      .collection-card {
        min-width: 0;
        background: var(--pb-surface);
        border: 1px solid var(--pb-line);
        border-radius: 16px;
        padding: 22px;
      }
      .collection-heading {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 20px;
      }
      .collection-heading h2 {
        margin-top: 0;
        font-size: 21px;
      }
      .collection-heading p {
        font-size: 12px;
        margin: 4px 0 7px;
      }
      .collection-images {
        display: flex;
        min-width: 100px;
        padding-left: 8px;
      }
      .collection-images img {
        width: 62px;
        height: 88px;
        object-fit: contain;
        border-radius: 12px;
        background: var(--secondary-background-color, #f2f5ef);
        border: 2px solid var(--pb-surface);
        margin-left: -8px;
      }
      .collection-card .counts {
        gap: 6px;
      }
      .collection-card .count {
        padding: 10px 8px;
      }
      .collection-card .count strong {
        font-size: 22px;
      }
      .members {
        margin-top: 18px;
      }
      .members summary {
        display: inline-flex;
        min-width: 150px;
        padding: 10px 14px;
        font-size: 13px;
        color: var(--pb-green);
      }
      .member-grid {
        margin-top: 14px;
      }
      .collection-link {
        margin-top: 10px;
      }
      .group-empty {
        font-size: 13px;
        padding: 16px 0 6px;
      }
      .section-title {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 0 0 16px;
      }
      .section-title h2 {
        margin: 0;
      }
      .section-title span {
        font-size: 12px;
        color: var(--pb-muted);
      }
      .area-section + .area-section {
        margin-top: 30px;
      }
      .feedback {
        padding: 18px 0 0;
      }
      .offline {
        font-size: 13px;
      }
      @media (max-width: 600px) {
        main {
          padding: 24px 16px 32px;
        }
        .toolbar {
          padding: 8px 12px;
        }
        .counts {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .controls {
          align-items: stretch;
          gap: 12px;
        }
        nav {
          width: 100%;
        }
        nav button {
          flex: 1;
        }
        .collection-card {
          padding: 16px;
        }
        .collection-images img {
          width: 48px;
        }
        .collection-images {
          min-width: 65px;
        }
        .plant {
          padding: 16px;
        }
      }
    `];
	}
}, $e = "config/config_entries/subentries/flow", et = { "HA-Frontend-Base": location.origin }, tt = class extends B {
	constructor(...e) {
		super(...e), this.areas = [], this._busy = !1, this._loading = !0, this._error = "", this.values = {}, this.labels = () => "", this.selectorLabels = () => "";
	}
	static {
		this.properties = {
			hass: { attribute: !1 },
			kind: { type: String },
			areas: { attribute: !1 },
			_step: { state: !0 },
			_busy: { state: !0 },
			_loading: { state: !0 },
			_error: { state: !0 }
		};
	}
	firstUpdated(e) {
		this.renderRoot.querySelector("dialog").showModal(), this.load();
	}
	disconnectedCallback() {
		super.disconnectedCallback(), this.discard();
	}
	async discard() {
		let e = this.flowId;
		if (this.flowId = void 0, e) try {
			await this.hass.callApi("DELETE", `${$e}/${encodeURIComponent(e)}`);
		} catch {}
	}
	close() {
		(!this._busy || this._loading) && this.dispatchEvent(new CustomEvent("closed", {
			bubbles: !0,
			composed: !0
		}));
	}
	async load() {
		if (!this._busy && this.hass.user?.is_admin) {
			this._busy = this._loading = !0, this._error = "";
			try {
				await this.discard();
				let e = (await this.hass.callWS({
					type: "config_entries/get",
					domain: "plantbased"
				})).find((e) => e.state === "loaded" && this.kind in e.supported_subentry_types);
				if (!e) throw Error("Hub not loaded");
				if (!this.isConnected) return;
				let t = await this.hass.callApi("POST", $e, { handler: [e.entry_id, this.kind] }, et);
				if (this.flowId = t.flow_id, !this.isConnected) {
					await this.discard();
					return;
				}
				if (this.labels = await this.hass.loadBackendTranslation("config_subentries", "plantbased"), this.selectorLabels = await this.hass.loadBackendTranslation("selector", "plantbased"), !this.isConnected) return;
				if (t.type !== "form" || !t.data_schema?.every((e) => [
					"text",
					"area",
					"number",
					"boolean",
					"date",
					"select"
				].some((t) => t in e.selector))) throw Error("Unexpected schema");
				this.values = Object.fromEntries(t.data_schema.map((e) => [e.name, e.description?.suggested_value ?? e.default ?? ("boolean" in e.selector ? !1 : "")])), this._step = t, this._loading = !1, this._busy = !1, await this.updateComplete, this.renderRoot.querySelector("input[name=\"name\"]")?.focus();
			} catch {
				this._error = V(this.hass, "createLoadError"), await this.discard();
			} finally {
				this._busy = !1;
			}
		}
	}
	label(e, t = "data") {
		return this.labels(`component.plantbased.config_subentries.${this.kind}.step.${this._step?.step_id ?? "user"}.${t}.${e.name}`) || (t === "data" ? e.name : "");
	}
	error(e) {
		let t = this._step?.errors?.[e];
		return t ? this.labels(`component.plantbased.config_subentries.${this.kind}.error.${t}`) || V(this.hass, "createError") : "";
	}
	field(e) {
		let t = e.name, n = e.selector, r = this.values[t] ?? "", i;
		if ("boolean" in n) i = A`<input
        id=${t}
        name=${t}
        type="checkbox"
        .checked=${r === !0}
      />`;
		else if (n.select || "area" in n) {
			let a = n.select?.options ?? this.areas.map((e) => ({
				value: e.area_id,
				label: e.name
			}));
			i = A`<select id=${t} name=${t} ?required=${e.required}>
        ${e.required ? N : A`<option value="" ?selected=${r === ""}>—</option>`}
        ${a.map((e) => {
				let t = typeof e == "string" ? e : e.value, i = n.select?.translation_key ? this.selectorLabels(`component.plantbased.selector.${n.select.translation_key}.options.${t}`) : "";
				return A`<option
            value=${t}
            ?selected=${String(r) === t}
          >
            ${i || (typeof e == "string" ? e : e.label)}
          </option>`;
			})}
      </select>`;
		} else i = n.text?.multiline ? A`<textarea
        id=${t}
        name=${t}
        .value=${String(r)}
        ?required=${e.required}
      ></textarea>` : A`<input
        id=${t}
        name=${t}
        type=${"number" in n ? "number" : "date" in n ? "date" : "text"}
        .value=${String(r)}
        ?required=${e.required}
        min=${n.number?.min ?? N}
        max=${n.number?.max ?? N}
        step=${n.number?.step ?? N}
      />`;
		let a = this.error(t), o = this.label(e, "data_description");
		return A`<div class="field ${"boolean" in n ? "boolean" : ""}">
      <label for=${t}
        >${this.label(e)}${e.required && !("boolean" in n) ? " *" : ""}</label
      >${i} ${o ? A`<p class="helper">${o}</p>` : N}
      ${a ? A`<p class="error" role="alert">${a}</p>` : N}
    </div>`;
	}
	async submit(e) {
		if (e.preventDefault(), this._busy || !this.flowId || !this.hass.user?.is_admin) return;
		let t = new FormData(e.currentTarget), n = {};
		for (let e of this._step?.data_schema ?? []) {
			let r = t.get(e.name);
			"boolean" in e.selector ? n[e.name] = t.has(e.name) : r !== null && r !== "" ? n[e.name] = "number" in e.selector ? Number(r) : r : e.required && (n[e.name] = "");
		}
		this.values = n, this._busy = !0, this._error = "";
		try {
			let e = await this.hass.callApi("POST", `${$e}/${encodeURIComponent(this.flowId)}`, n, et);
			if (!this.isConnected) return;
			e.type === "create_entry" ? (this.flowId = void 0, this.dispatchEvent(new CustomEvent("created", {
				bubbles: !0,
				composed: !0
			}))) : e.type === "form" ? this._step = e : (this.flowId = void 0, this._loading = !0, this._error = V(this.hass, "createError"));
		} catch {
			this._error = V(this.hass, "createError");
		} finally {
			this._busy = !1;
		}
	}
	render() {
		return A`<dialog
      aria-labelledby="create-title"
      @cancel=${(e) => {
			e.preventDefault(), this.close();
		}}
    >
      <h2 id="create-title">
        ${V(this.hass, this.kind === "plant" ? "addPlant" : "addGroup")}
      </h2>
      ${this._error ? A`<p class="error" role="alert">${this._error}</p>` : N}
      ${this._loading ? A`<p role="status">
                ${this._error ? "" : V(this.hass, "loading")}
              </p>
              <div class="dialog-actions">
                ${this._error ? A`<button ?disabled=${this._busy} @click=${() => this.load()}>${V(this.hass, "retry")}</button>` : N}<button
                  @click=${() => this.close()}
                >
                  ${V(this.hass, "cancel")}
                </button>
              </div>` : A`<form @submit=${this.submit}>
              <fieldset ?disabled=${this._busy}>
                <div class="fields">
                  ${this._step?.data_schema?.map((e) => this.field(e))}
                </div>
                ${this.error("base") ? A`<p class="error" role="alert">${this.error("base")}</p>` : N}
              </fieldset>
              <div class="dialog-actions">
                <button
                  type="button"
                  ?disabled=${this._busy}
                  @click=${() => this.close()}
                >
                  ${V(this.hass, "cancel")}</button
                ><button class="primary" type="submit" ?disabled=${this._busy}>
                  ${V(this.hass, "create")}
                </button>
              </div>
            </form>`}
    </dialog>`;
	}
	static {
		this.styles = [J, o`
      dialog[open] {
        display: flex;
        flex-direction: column;
      }
      dialog {
        width: min(680px, calc(100vw - 32px));
        max-height: 85vh;
        max-height: 85dvh;
        border: 1px solid var(--pb-line);
        border-radius: 18px;
        padding: 24px;
        background: var(--pb-surface);
        color: var(--primary-text-color, #263b31);
        box-shadow: 0 12px 48px #0003;
        overflow: hidden;
      }
      dialog::backdrop {
        background: #0006;
      }
      h2 {
        margin: 0 0 20px;
        flex-shrink: 0;
      }
      form {
        display: flex;
        flex-direction: column;
        min-height: 0;
      }
      fieldset {
        padding: 0;
        margin: 0;
        border: 0;
        min-width: 0;
        min-height: 0;
        overflow: auto;
        padding: 4px;
      }
      .fields {
        display: grid;
        gap: 16px;
      }
      .field {
        min-width: 0;
      }
      label {
        margin: 0 0 6px;
      }
      input:not([type="checkbox"]),
      textarea,
      select {
        width: 100%;
        min-height: 44px;
        font: inherit;
        padding: 10px;
        border: 1px solid var(--pb-line);
        border-radius: 10px;
        color: inherit;
        background: var(--pb-surface);
      }
      textarea {
        min-height: 80px;
        resize: vertical;
      }
      .helper {
        margin: 5px 0 0;
        font-size: 12px;
      }
      .error {
        margin: 7px 0;
        font-size: 13px;
      }
      .boolean {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .boolean label {
        margin: 0;
      }
      .dialog-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 22px;
        flex-shrink: 0;
      }
    `];
	}
};
//#endregion
//#region frontend/src/index.ts
for (let [e, t] of [
	["plantbased-card", Le],
	["plantbased-overview-card", Re],
	["plantbased-card-editor", ze],
	["plantbased-overview-card-editor", Be],
	["plantbased-panel", Qe],
	["plantbased-create-dialog", tt]
]) customElements.get(e) || customElements.define(e, t);
var nt = window;
nt.customCards ??= [];
for (let [e, t, n] of [[
	"plantbased-card",
	"PlantBased",
	"Pflanzenpflege · Plant care"
], [
	"plantbased-overview-card",
	"PlantBased Overview / Übersicht",
	"Pflanzenübersicht · Plant overview"
]]) nt.customCards.some((t) => t.type === e) || nt.customCards.push({
	type: e,
	name: t,
	description: n,
	preview: !0,
	documentationURL: "https://github.com/Pyromania522/PlantBased"
});
//#endregion
