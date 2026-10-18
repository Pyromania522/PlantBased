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
}, re = (e, t) => !l(e, t), v = {
	attribute: !0,
	type: String,
	converter: _,
	reflect: !1,
	useDefault: !1,
	hasChanged: re
};
Symbol.metadata ??= Symbol("metadata"), h.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
var y = class extends HTMLElement {
	static addInitializer(e) {
		this._$Ei(), (this.l ??= []).push(e);
	}
	static get observedAttributes() {
		return this.finalize(), this._$Eh && [...this._$Eh.keys()];
	}
	static createProperty(e, t = v) {
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
		return this.elementProperties.get(e) ?? v;
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
y.elementStyles = [], y.shadowRootOptions = { mode: "open" }, y[g("elementProperties")] = /* @__PURE__ */ new Map(), y[g("finalized")] = /* @__PURE__ */ new Map(), ne?.({ ReactiveElement: y }), (h.reactiveElementVersions ??= []).push("2.1.2");
//#endregion
//#region node_modules/lit-html/lit-html.js
var b = globalThis, ie = (e) => e, x = b.trustedTypes, ae = x ? x.createPolicy("lit-html", { createHTML: (e) => e }) : void 0, S = "$lit$", C = `lit$${Math.random().toFixed(9).slice(2)}$`, oe = "?" + C, se = `<${oe}>`, w = document, T = () => w.createComment(""), E = (e) => e === null || typeof e != "object" && typeof e != "function", D = Array.isArray, ce = (e) => D(e) || typeof e?.[Symbol.iterator] == "function", O = "[ 	\n\f\r]", k = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, A = /-->/g, j = />/g, M = RegExp(`>|${O}(?:([^\\s"'>=/]+)(${O}*=${O}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"), N = /'/g, le = /"/g, ue = /^(?:script|style|textarea|title)$/i, de = (e) => (t, ...n) => ({
	_$litType$: e,
	strings: t,
	values: n
}), P = de(1), F = de(2), I = Symbol.for("lit-noChange"), L = Symbol.for("lit-nothing"), fe = /* @__PURE__ */ new WeakMap(), R = w.createTreeWalker(w, 129);
function pe(e, t) {
	if (!D(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
	return ae === void 0 ? t : ae.createHTML(t);
}
var me = (e, t) => {
	let n = e.length - 1, r = [], i, a = t === 2 ? "<svg>" : t === 3 ? "<math>" : "", o = k;
	for (let t = 0; t < n; t++) {
		let n = e[t], s, c, l = -1, u = 0;
		for (; u < n.length && (o.lastIndex = u, c = o.exec(n), c !== null);) u = o.lastIndex, o === k ? c[1] === "!--" ? o = A : c[1] === void 0 ? c[2] === void 0 ? c[3] !== void 0 && (o = M) : (ue.test(c[2]) && (i = RegExp("</" + c[2], "g")), o = M) : o = j : o === M ? c[0] === ">" ? (o = i ?? k, l = -1) : c[1] === void 0 ? l = -2 : (l = o.lastIndex - c[2].length, s = c[1], o = c[3] === void 0 ? M : c[3] === "\"" ? le : N) : o === le || o === N ? o = M : o === A || o === j ? o = k : (o = M, i = void 0);
		let d = o === M && e[t + 1].startsWith("/>") ? " " : "";
		a += o === k ? n + se : l >= 0 ? (r.push(s), n.slice(0, l) + S + n.slice(l) + C + d) : n + C + (l === -2 ? t : d);
	}
	return [pe(e, a + (e[n] || "<?>") + (t === 2 ? "</svg>" : t === 3 ? "</math>" : "")), r];
}, z = class e {
	constructor({ strings: t, _$litType$: n }, r) {
		let i;
		this.parts = [];
		let a = 0, o = 0, s = t.length - 1, c = this.parts, [l, u] = me(t, n);
		if (this.el = e.createElement(l, r), R.currentNode = this.el.content, n === 2 || n === 3) {
			let e = this.el.content.firstChild;
			e.replaceWith(...e.childNodes);
		}
		for (; (i = R.nextNode()) !== null && c.length < s;) {
			if (i.nodeType === 1) {
				if (i.hasAttributes()) for (let e of i.getAttributeNames()) if (e.endsWith(S)) {
					let t = u[o++], n = i.getAttribute(e).split(C), r = /([.?@])?(.*)/.exec(t);
					c.push({
						type: 1,
						index: a,
						name: r[2],
						strings: n,
						ctor: r[1] === "." ? ge : r[1] === "?" ? _e : r[1] === "@" ? ve : H
					}), i.removeAttribute(e);
				} else e.startsWith(C) && (c.push({
					type: 6,
					index: a
				}), i.removeAttribute(e));
				if (ue.test(i.tagName)) {
					let e = i.textContent.split(C), t = e.length - 1;
					if (t > 0) {
						i.textContent = x ? x.emptyScript : "";
						for (let n = 0; n < t; n++) i.append(e[n], T()), R.nextNode(), c.push({
							type: 2,
							index: ++a
						});
						i.append(e[t], T());
					}
				}
			} else if (i.nodeType === 8) {
				if (i.data === oe) c.push({
					type: 2,
					index: a
				});
				else {
					let e = -1;
					for (; (e = i.data.indexOf(C, e + 1)) !== -1;) c.push({
						type: 7,
						index: a
					}), e += C.length - 1;
				}
			}
			a++;
		}
	}
	static createElement(e, t) {
		let n = w.createElement("template");
		return n.innerHTML = e, n;
	}
};
function B(e, t, n = e, r) {
	if (t === I) return t;
	let i = r === void 0 ? n._$Cl : n._$Co?.[r], a = E(t) ? void 0 : t._$litDirective$;
	return i?.constructor !== a && (i?._$AO?.(!1), a === void 0 ? i = void 0 : (i = new a(e), i._$AT(e, n, r)), r === void 0 ? n._$Cl = i : (n._$Co ??= [])[r] = i), i !== void 0 && (t = B(e, i._$AS(e, t.values), i, r)), t;
}
var he = class {
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
		let { el: { content: t }, parts: n } = this._$AD, r = (e?.creationScope ?? w).importNode(t, !0);
		R.currentNode = r;
		let i = R.nextNode(), a = 0, o = 0, s = n[0];
		for (; s !== void 0;) {
			if (a === s.index) {
				let t;
				s.type === 2 ? t = new V(i, i.nextSibling, this, e) : s.type === 1 ? t = new s.ctor(i, s.name, s.strings, this, e) : s.type === 6 && (t = new ye(i, this, e)), this._$AV.push(t), s = n[++o];
			}
			a !== s?.index && (i = R.nextNode(), a++);
		}
		return R.currentNode = w, r;
	}
	p(e) {
		let t = 0;
		for (let n of this._$AV) n !== void 0 && (n.strings === void 0 ? n._$AI(e[t]) : (n._$AI(e, n, t), t += n.strings.length - 2)), t++;
	}
}, V = class e {
	get _$AU() {
		return this._$AM?._$AU ?? this._$Cv;
	}
	constructor(e, t, n, r) {
		this.type = 2, this._$AH = L, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = n, this.options = r, this._$Cv = r?.isConnected ?? !0;
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
		e = B(this, e, t), E(e) ? e === L || e == null || e === "" ? (this._$AH !== L && this._$AR(), this._$AH = L) : e !== this._$AH && e !== I && this._(e) : e._$litType$ === void 0 ? e.nodeType === void 0 ? ce(e) ? this.k(e) : this._(e) : this.T(e) : this.$(e);
	}
	O(e) {
		return this._$AA.parentNode.insertBefore(e, this._$AB);
	}
	T(e) {
		this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
	}
	_(e) {
		this._$AH !== L && E(this._$AH) ? this._$AA.nextSibling.data = e : this.T(w.createTextNode(e)), this._$AH = e;
	}
	$(e) {
		let { values: t, _$litType$: n } = e, r = typeof n == "number" ? this._$AC(e) : (n.el === void 0 && (n.el = z.createElement(pe(n.h, n.h[0]), this.options)), n);
		if (this._$AH?._$AD === r) this._$AH.p(t);
		else {
			let e = new he(r, this), n = e.u(this.options);
			e.p(t), this.T(n), this._$AH = e;
		}
	}
	_$AC(e) {
		let t = fe.get(e.strings);
		return t === void 0 && fe.set(e.strings, t = new z(e)), t;
	}
	k(t) {
		D(this._$AH) || (this._$AH = [], this._$AR());
		let n = this._$AH, r, i = 0;
		for (let a of t) i === n.length ? n.push(r = new e(this.O(T()), this.O(T()), this, this.options)) : r = n[i], r._$AI(a), i++;
		i < n.length && (this._$AR(r && r._$AB.nextSibling, i), n.length = i);
	}
	_$AR(e = this._$AA.nextSibling, t) {
		for (this._$AP?.(!1, !0, t); e !== this._$AB;) {
			let t = ie(e).nextSibling;
			ie(e).remove(), e = t;
		}
	}
	setConnected(e) {
		this._$AM === void 0 && (this._$Cv = e, this._$AP?.(e));
	}
}, H = class {
	get tagName() {
		return this.element.tagName;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	constructor(e, t, n, r, i) {
		this.type = 1, this._$AH = L, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = i, n.length > 2 || n[0] !== "" || n[1] !== "" ? (this._$AH = Array(n.length - 1).fill(/* @__PURE__ */ new String()), this.strings = n) : this._$AH = L;
	}
	_$AI(e, t = this, n, r) {
		let i = this.strings, a = !1;
		if (i === void 0) e = B(this, e, t, 0), a = !E(e) || e !== this._$AH && e !== I, a && (this._$AH = e);
		else {
			let r = e, o, s;
			for (e = i[0], o = 0; o < i.length - 1; o++) s = B(this, r[n + o], t, o), s === I && (s = this._$AH[o]), a ||= !E(s) || s !== this._$AH[o], s === L ? e = L : e !== L && (e += (s ?? "") + i[o + 1]), this._$AH[o] = s;
		}
		a && !r && this.j(e);
	}
	j(e) {
		e === L ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
	}
}, ge = class extends H {
	constructor() {
		super(...arguments), this.type = 3;
	}
	j(e) {
		this.element[this.name] = e === L ? void 0 : e;
	}
}, _e = class extends H {
	constructor() {
		super(...arguments), this.type = 4;
	}
	j(e) {
		this.element.toggleAttribute(this.name, !!e && e !== L);
	}
}, ve = class extends H {
	constructor(e, t, n, r, i) {
		super(e, t, n, r, i), this.type = 5;
	}
	_$AI(e, t = this) {
		if ((e = B(this, e, t, 0) ?? L) === I) return;
		let n = this._$AH, r = e === L && n !== L || e.capture !== n.capture || e.once !== n.once || e.passive !== n.passive, i = e !== L && (n === L || r);
		r && this.element.removeEventListener(this.name, this, n), i && this.element.addEventListener(this.name, this, e), this._$AH = e;
	}
	handleEvent(e) {
		typeof this._$AH == "function" ? this._$AH.call(this.options?.host ?? this.element, e) : this._$AH.handleEvent(e);
	}
}, ye = class {
	constructor(e, t, n) {
		this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = n;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	_$AI(e) {
		B(this, e);
	}
}, be = b.litHtmlPolyfillSupport;
be?.(z, V), (b.litHtmlVersions ??= []).push("3.3.3");
var xe = (e, t, n) => {
	let r = n?.renderBefore ?? t, i = r._$litPart$;
	if (i === void 0) {
		let e = n?.renderBefore ?? null;
		r._$litPart$ = i = new V(t.insertBefore(T(), e), e, void 0, n ?? {});
	}
	return i._$AI(e), i;
}, U = globalThis, W = class extends y {
	constructor() {
		super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
	}
	createRenderRoot() {
		let e = super.createRenderRoot();
		return this.renderOptions.renderBefore ??= e.firstChild, e;
	}
	update(e) {
		let t = this.render();
		this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = xe(t, this.renderRoot, this.renderOptions);
	}
	connectedCallback() {
		super.connectedCallback(), this._$Do?.setConnected(!0);
	}
	disconnectedCallback() {
		super.disconnectedCallback(), this._$Do?.setConnected(!1);
	}
	render() {
		return I;
	}
};
W._$litElement$ = !0, W.finalized = !0, U.litElementHydrateSupport?.({ LitElement: W });
var Se = U.litElementPolyfillSupport;
Se?.({ LitElement: W }), (U.litElementVersions ??= []).push("4.2.2");
//#endregion
//#region frontend/src/localize.ts
var Ce = {
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
}, we = {
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
}, Te = (e) => (e?.locale?.language ?? e?.language ?? "en").toLowerCase().startsWith("de") ? "de" : "en", G = (e, t, n) => (Te(e) === "de" ? we : Ce)[t].replace("{n}", String(n ?? ""));
function Ee(e, t) {
	return t === null ? G(e, "unavailable") : t === 0 ? G(e, "today") : t === 1 ? G(e, "tomorrow") : t === -1 ? G(e, "overdueDay") : G(e, t < 0 ? "overdueDays" : "days", Math.abs(t));
}
//#endregion
//#region frontend/src/model.ts
var De = [
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
function K(e) {
	let t = new URL(import.meta.url), n = new URL(`illustrations/${De.includes(e) ? e : "generic"}.svg`, t);
	return n.search = new URL(import.meta.url).search, n.href;
}
function Oe(e, t) {
	if (typeof e != "string") return K(t);
	try {
		if (e.startsWith("/local/") || e.startsWith("/plantbased/illustrations/")) return new URL(e, location.origin).href;
		let t = new URL(e);
		if (["http:", "https:"].includes(t.protocol) && !t.username && !t.password) return t.href;
	} catch {}
	return K(t);
}
function ke(e, t = !1, n) {
	if (!e || typeof e != "object" || !t && e.device_id !== void 0 && typeof e.device_id != "string") throw Error(G(n, "invalidConfig"));
	if (e.title !== void 0 && typeof e.title != "string") throw Error(G(n, "invalidTitle"));
	if (e.show_actions !== void 0 && typeof e.show_actions != "boolean") throw Error(G(n, "invalidActions"));
	return { ...e };
}
var q = (e) => e.name_by_user || e.name || "PlantBased";
function J(e) {
	return e.translation_key || e.unique_id.slice((e.config_subentry_id || e.config_entry_id || "").length + 1);
}
function Y(e, t, n, r) {
	let i = t.entities.find((e) => e.device_id === n && J(e) === r && !e.disabled_by);
	return i ? e.states[i.entity_id] : void 0;
}
function X(e) {
	if (!e || [
		"unknown",
		"unavailable",
		""
	].includes(e.state)) return null;
	let t = Number(e.state);
	return Number.isFinite(t) ? t : null;
}
function Ae(e, t) {
	return t.devices.filter((e) => e.model === "Plant").map((n) => {
		let r = t.entities.filter((e) => e.device_id === n.id), i = Y(e, t, n.id, "care_status"), a = i?.attributes ?? {}, o = r.find((e) => e.config_subentry_id)?.config_subentry_id ?? String(a.subentry_id ?? ""), s = !!i && [
			"ok",
			"water",
			"fertilize",
			"water_and_fertilize",
			"paused"
		].includes(i.state) && !n.disabled_by && e.connected !== !1, c = s && ["water", "water_and_fertilize"].includes(i.state), l = s && ["fertilize", "water_and_fertilize"].includes(i.state), u = X(Y(e, t, n.id, "days_until_watering")), d = X(Y(e, t, n.id, "days_until_fertilizing")), f = s ? i.state : "unavailable", p = s ? f === "paused" ? "paused" : c && u !== null && u < 0 || l && d !== null && d < 0 ? "overdue" : c || l ? "due" : "ok" : "unavailable", m = typeof a.image_preset == "string" ? a.image_preset : "generic";
		return {
			deviceId: n.id,
			subentryId: o,
			name: q(n),
			group: typeof a.group == "string" ? a.group : null,
			groupId: typeof a.group_id == "string" ? a.group_id : null,
			image: Oe(a.image_url, m),
			preset: m,
			status: f,
			tone: p,
			available: s,
			waterDue: c,
			fertilizerDue: l,
			waterDays: u,
			fertilizerDays: d,
			fertilizingEnabled: a.fertilizing_enabled !== !1
		};
	}).sort((e, t) => e.name.localeCompare(t.name));
}
function je(e, t) {
	return [
		"total_plants",
		"plants_needing_water",
		"plants_needing_fertilizer",
		"plants_overdue"
	].map((n) => {
		let r = t.entities.find((e) => !e.config_subentry_id && J(e) === n && !e.disabled_by);
		return e.connected === !1 ? null : X(r ? e.states[r.entity_id] : void 0);
	});
}
//#endregion
//#region frontend/src/registry.ts
var Z = class {
	constructor(e) {
		this.host = e, this.error = !1, this.connected = !1, this.generation = 0, this.unsubs = [], this.loading = !1, this.dirty = !1, this.onReady = () => {
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
		for (let n of ["entity_registry_updated", "device_registry_updated"]) e.subscribeEvents(this.onReady, n).then((e) => {
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
			let [t, n] = await Promise.all([this.hass.callWS({ type: "config/entity_registry/list" }), this.hass.callWS({ type: "config/device_registry/list" })]);
			if (e !== this.generation) return;
			this.data = {
				entities: t.filter((e) => e.platform === "plantbased"),
				devices: n.filter((e) => e.identifiers.some(([e]) => e === "plantbased"))
			}, this.error = !1;
		} catch {
			e === this.generation && (this.error = !0);
		} finally {
			e === this.generation && (this.loading = !1, this.host.requestUpdate(), this.dirty && (this.dirty = !1, this.refresh()));
		}
	}
}, Me = o`
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
`, Q = (e) => P`<svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    ${e === "water" ? F`<path d="M12 3C9 7 5 11 5 15a7 7 0 0 0 14 0c0-4-4-8-7-12Z"/><path d="M8 15a4 4 0 0 0 4 4"/>` : e === "leaf" ? F`<path d="M5 20 17 8M5 16C2 6 12 3 21 3c0 9-3 19-13 16"/>` : e === "clock" ? F`<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>` : F`<path d="M7 15h10l-1 6H8l-1-6ZM12 15V6M12 11C4 12 4 5 4 4c6-1 8 3 8 7ZM12 9c0-5 4-6 8-6 0 5-3 8-8 6Z"/>`}
  </svg>`, Ne = class extends W {
	constructor(...e) {
		super(...e), this._message = "", this._error = !1, this.pending = /* @__PURE__ */ new Set(), this.registry = new Z(this);
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
		this.styles = Me;
	}
	setConfig(e) {
		this._config = ke(e, this.overview, this.hass);
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
		return this.registry.error ? P`<div class="empty" role="alert">
        <p>${G(this.hass, "registryError")}</p>
        <button @click=${() => this.registry.refresh()}>
          ${G(this.hass, "retry")}
        </button>
      </div>` : !this.hass || !this.registry.data ? P`<div class="empty" role="status">
        ${G(this.hass, "loading")}
      </div>` : L;
	}
	feedback() {
		return P`<div
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
				} : {}, { device_id: e.deviceId }, !1), this._message = G(this.hass, "saved"), this._error = !1;
			} catch {
				this._message = G(this.hass, "actionError"), this._error = !0;
			} finally {
				this.pending.delete(e.deviceId), this.requestUpdate();
			}
		}
	}
	row(e) {
		let t = this.pending.has(e.deviceId) || !e.available, n = e.tone === "paused";
		return P`<article
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
			let n = t.currentTarget, r = K(e.preset);
			n.src !== r && (n.src = r);
		}}
        />
        <div>
          <h3>${e.name}</h3>
          ${e.group ? P`<p class="plant-group">${e.group}</p>` : L}<span
            class="badge ${e.tone}"
            >${G(this.hass, e.tone)}</span
          >
        </div>
      </div>
      <div class="chips">
        <div class="chip ${e.waterDue && !n ? "active" : ""}">
          <span class="chip-label"
            >${Q("water")}${G(this.hass, "water")}</span
          ><span class="chip-value"
            >${Ee(this.hass, e.available ? e.waterDays : null)}</span
          >
        </div>
        <div class="chip ${e.fertilizerDue && !n ? "active" : ""}">
          <span class="chip-label"
            >${Q("leaf")}${G(this.hass, "fertilize")}</span
          ><span class="chip-value"
            >${e.fertilizingEnabled ? Ee(this.hass, e.available ? e.fertilizerDays : null) : G(this.hass, "disabled")}</span
          >
        </div>
      </div>
      ${this._config?.show_actions === !1 ? L : P`<div class="actions">
              <button
                class="primary"
                ?disabled=${t}
                @click=${() => this.act(e, "mark_watered")}
              >
                ${Q("water")}${G(this.hass, "watered")}
              </button>
              <button
                ?disabled=${t || !e.fertilizingEnabled}
                @click=${() => this.act(e, "mark_fertilized")}
              >
                ${Q("leaf")}${G(this.hass, "fertilized")}
              </button>
              ${t ? P`<button disabled aria-label=${G(this.hass, "snooze")}>
                      ${Q("clock")}
                    </button>` : P`<details>
                      <summary
                        aria-label=${G(this.hass, "snooze")}
                        title=${G(this.hass, "snooze")}
                      >
                        ${Q("clock")}
                      </summary>
                      <div class="snooze-menu">
                        <button
                          @click=${() => this.act(e, "snooze", "water")}
                        >
                          ${G(this.hass, "snoozeWater")}</button
                        >${e.fertilizingEnabled ? P`<button @click=${() => this.act(e, "snooze", "fertilize")}>${G(this.hass, "snoozeFertilizer")}</button>` : L}
                      </div>
                    </details>`}
            </div>`}
    </article>`;
	}
	empty(e, t) {
		return P`<div class="empty">
      <img src=${K("generic")} alt="" />
      <h3>${G(this.hass, e)}</h3>
      <p>${G(this.hass, t)}</p>
    </div>`;
	}
}, Pe = class extends Ne {
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
		if (!this.hass || !this.registry.data || this.registry.error) return P`<ha-card>${this.renderStatus()}</ha-card>`;
		let e = this.registry.data, t = e.devices.find((e) => e.id === this._config?.device_id && ["Plant", "Group"].includes(e.model ?? ""));
		if (!t) return P`<ha-card
        >${this.empty(this._config?.device_id ? "missingDevice" : "chooseDevice", "noDevices")}</ha-card
      >`;
		let n = t.model === "Group", r = e.entities.find((e) => e.device_id === t.id && e.config_subentry_id)?.config_subentry_id, i = Ae(this.hass, e).filter((e) => n ? e.groupId === r : e.deviceId === t.id);
		return P`<ha-card
      ><header class="header">
        <div class="brand">PlantBased</div>
        ${this._config?.title || n ? P`<h2>${this._config?.title || q(t)}</h2>` : L}${n ? P`<p>${i.length} ${G(this.hass, i.length === 1 ? "plant" : "plants")}</p>` : L}
      </header>
      ${i.length ? P`<div class=${n ? "grid" : "single"}>${i.map((e) => this.row(e))}</div>` : P`<div class="empty"><p>${G(this.hass, "groupEmpty")}</p></div>`}${this.feedback()}</ha-card
    >`;
	}
}, Fe = class extends Ne {
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
		if (!this.hass || !this.registry.data || this.registry.error) return P`<ha-card>${this.renderStatus()}</ha-card>`;
		let e = Ae(this.hass, this.registry.data), t = e.filter((e) => e.waterDue || e.fertilizerDue).sort((e, t) => Number(t.tone === "overdue") - Number(e.tone === "overdue") || e.name.localeCompare(t.name)), n = je(this.hass, this.registry.data), r = [
			"total",
			"water",
			"fertilize",
			"overdue"
		], i = [
			"plants",
			"water",
			"leaf",
			"clock"
		], a = this.registry.data.entities.some((e) => !e.config_subentry_id && J(e) === "total_plants");
		return P`<ha-card
      ><header class="header">
        <div class="brand">PlantBased</div>
        <h2>${this._config?.title || G(this.hass, "overview")}</h2>
      </header>
      <div class="counts">
        ${r.map((e, t) => P`<div class="count ${e}" aria-label=${G(this.hass, e)}><span>${Q(i[t])}${G(this.hass, e)}</span><strong>${n[t] ?? "—"}</strong></div>`)}
      </div>
      ${e.length ? !a || n.some((e) => e === null) ? P`<div class="empty"><p>${G(this.hass, "unavailable")}</p></div>` : t.length ? P`<div class="overview-list">${t.map((e) => this.row(e))}</div>` : this.empty("allDone", "allDoneHint") : this.empty("noPlants", "noPlantsHint")}${this.feedback()}</ha-card
    >`;
	}
}, Ie = class extends W {
	constructor(...e) {
		super(...e), this._config = { type: "custom:plantbased-card" }, this.overview = !1, this.registry = new Z(this);
	}
	static {
		this.properties = {
			hass: { attribute: !1 },
			_config: { state: !0 }
		};
	}
	static {
		this.styles = Me;
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
		let e = this.registry.data?.devices.filter((e) => ["Plant", "Group"].includes(e.model ?? "")).sort((e, t) => q(e).localeCompare(q(t))) ?? [], t = this._config.device_id && !e.some((e) => e.id === this._config.device_id);
		return P`<div class="editor">
      ${this.overview ? L : P`<label for="device">${G(this.hass, "chooseDevice")}</label
              ><select
                id="device"
                .value=${this._config.device_id || ""}
                @change=${(e) => this.change("device_id", e.currentTarget.value)}
              >
                <option value="">${G(this.hass, "chooseDevice")}</option>
                ${t ? P`<option value=${this._config.device_id}>${G(this.hass, "unavailable")}</option>` : L}${e.map((e) => P`<option value=${e.id}>${q(e)} · ${G(this.hass, e.model === "Plant" ? "plant" : "group")}</option>`)}</select
              >${e.length ? L : P`<p>${G(this.hass, this.registry.data ? "noDevices" : "loading")}</p>`}${this.registry.error ? P`<p role="alert">${G(this.hass, "registryError")}</p>
                      <button @click=${() => this.registry.refresh()}>
                        ${G(this.hass, "retry")}
                      </button>` : L}`} <label for="title">${G(this.hass, "title")}</label
      ><input
        id="title"
        type="text"
        placeholder=${G(this.hass, "titleHint")}
        .value=${this._config.title ?? ""}
        @input=${(e) => this.change("title", e.currentTarget.value)}
      />
      <label class="check"
        ><input
          type="checkbox"
          .checked=${this._config.show_actions !== !1}
          @change=${(e) => this.change("show_actions", e.currentTarget.checked)}
        />${G(this.hass, "showActions")}</label
      >
    </div>`;
	}
}, Le = class extends Ie {
	constructor(...e) {
		super(...e), this.overview = !0;
	}
};
//#endregion
//#region frontend/src/index.ts
for (let [e, t] of [
	["plantbased-card", Pe],
	["plantbased-overview-card", Fe],
	["plantbased-card-editor", Ie],
	["plantbased-overview-card-editor", Le]
]) customElements.get(e) || customElements.define(e, t);
var $ = window;
$.customCards ??= [];
for (let [e, t, n] of [[
	"plantbased-card",
	"PlantBased",
	"Pflanzenpflege · Plant care"
], [
	"plantbased-overview-card",
	"PlantBased Overview / Übersicht",
	"Pflanzenübersicht · Plant overview"
]]) $.customCards.some((t) => t.type === e) || $.customCards.push({
	type: e,
	name: t,
	description: n,
	preview: !0,
	documentationURL: "https://github.com/Pyromania522/PlantBased"
});
//#endregion
