(function () {
  "use strict";

  var KEY = "mehrBakeryTestInbox";

  // ---------- storage (browser only, nothing is sent anywhere) ----------
  function loadEnquiries() {
    try {
      var raw = window.localStorage.getItem(KEY);
      var data = raw ? JSON.parse(raw) : [];
      return Array.isArray(data) ? data : [];
    } catch (e) {
      return [];
    }
  }

  function writeAll(list) {
    window.localStorage.setItem(KEY, JSON.stringify(list));
  }

  function saveEnquiry(entry) {
    var list = loadEnquiries();
    list.push(entry);
    writeAll(list); // may throw; callers handle it
  }

  function deleteEnquiry(id) {
    writeAll(loadEnquiries().filter(function (e) { return e.id !== id; }));
  }

  function clearEnquiries() {
    writeAll([]);
  }

  // ---------- validation ----------
  var NAME_RE = /^[\p{L}][\p{L}\p{M} .'\-]*$/u;

  function validateName(v) {
    v = v.trim();
    if (v.length < 2 || v.length > 60 || !NAME_RE.test(v)) {
      return "Please enter your name (2 to 60 letters).";
    }
    return "";
  }

  function validatePhone(v) {
    var s = v.replace(/[\s\-()]/g, "");
    if (/^03\d{9}$/.test(s) || /^\+923\d{9}$/.test(s)) return "";
    return "Enter a Pakistani mobile number, like 0300 0000000 or +92 300 0000000.";
  }

  function validateMessage(v) {
    v = v.trim();
    if (v.length < 10 || v.length > 1000) {
      return "Please write at least 10 characters about your order (up to 1000).";
    }
    return "";
  }

  // ---------- form page ----------
  var form = document.getElementById("enquiry-form");
  if (form) {
    var fields = [
      { el: form.elements.name, err: document.getElementById("name-error"), check: validateName },
      { el: form.elements.phone, err: document.getElementById("phone-error"), check: validatePhone },
      { el: form.elements.message, err: document.getElementById("message-error"), check: validateMessage }
    ];
    var status = document.getElementById("status");
    var count = document.getElementById("count");

    var showError = function (f, touchedOnly) {
      var msg = f.check(f.el.value);
      f.err.textContent = msg;
      if (msg) f.el.setAttribute("aria-invalid", "true");
      else f.el.removeAttribute("aria-invalid");
      return msg;
    };

    fields.forEach(function (f) {
      f.touched = false;
      f.el.addEventListener("blur", function () { f.touched = true; showError(f); });
      f.el.addEventListener("input", function () { if (f.touched) showError(f); });
    });

    form.elements.message.addEventListener("input", function () {
      count.textContent = form.elements.message.value.length;
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      status.textContent = "";
      status.className = "status";

      var firstBad = null;
      fields.forEach(function (f) {
        f.touched = true;
        if (showError(f) && !firstBad) firstBad = f.el;
      });
      if (firstBad) { firstBad.focus(); return; }

      var entry = {
        id: Date.now() + "-" + Math.random().toString(36).slice(2, 8),
        name: form.elements.name.value.trim(),
        phone: form.elements.phone.value.trim(),
        message: form.elements.message.value.trim(),
        createdAt: new Date().toISOString()
      };

      try {
        saveEnquiry(entry);
      } catch (e) {
        status.className = "status bad";
        status.textContent = "Could not save in this browser (storage may be blocked). Your text is still here.";
        return;
      }

      form.reset();
      count.textContent = "0";
      fields.forEach(function (f) {
        f.touched = false;
        f.err.textContent = "";
        f.el.removeAttribute("aria-invalid");
      });
      status.className = "status ok";
      status.textContent = "Saved in this browser only. Nothing was sent. ";
      var link = document.createElement("a");
      link.href = "inbox.html";
      link.textContent = "Open the test inbox";
      status.appendChild(link);
    });
  }

  // ---------- inbox page ----------
  var list = document.getElementById("inbox-list");
  if (list) {
    var countEl = document.getElementById("inbox-count");
    var emptyEl = document.getElementById("inbox-empty");
    var clearBtn = document.getElementById("clear-all");

    var render = function () {
      var items = loadEnquiries().slice().reverse();
      list.textContent = "";
      countEl.textContent = items.length + (items.length === 1 ? " enquiry" : " enquiries");
      emptyEl.hidden = items.length > 0;
      clearBtn.hidden = items.length === 0;

      items.forEach(function (e) {
        var box = document.createElement("article");
        box.className = "entry";

        var h = document.createElement("h3");
        h.textContent = String(e.name || "");
        box.appendChild(h);

        var when = document.createElement("div");
        when.className = "when";
        var d = new Date(e.createdAt);
        when.textContent = isNaN(d) ? "" : d.toLocaleString();
        box.appendChild(when);

        var phoneP = document.createElement("p");
        var a = document.createElement("a");
        var phone = String(e.phone || "");
        a.textContent = phone;
        a.href = "tel:" + phone.replace(/[^\d+]/g, "");
        phoneP.appendChild(a);
        box.appendChild(phoneP);

        var msg = document.createElement("p");
        msg.className = "msg";
        msg.textContent = String(e.message || "");
        box.appendChild(msg);

        var del = document.createElement("button");
        del.type = "button";
        del.className = "btn ghost small";
        del.textContent = "Delete";
        del.addEventListener("click", function () {
          try { deleteEnquiry(e.id); } catch (err) {}
          render();
        });
        box.appendChild(del);

        list.appendChild(box);
      });
    };

    clearBtn.addEventListener("click", function () {
      if (window.confirm("Delete all test enquiries?")) {
        try { clearEnquiries(); } catch (err) {}
        render();
      }
    });

    window.addEventListener("storage", function (ev) { if (ev.key === KEY) render(); });
    render();
  }
})();
