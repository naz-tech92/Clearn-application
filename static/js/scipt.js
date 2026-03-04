// Compatibility shim for accidental references to "scipt.js" (typo).
// Loads the canonical site script.
(function loadCanonicalScript() {
    var s = document.createElement("script");
    s.src = "/static/js/script.js";
    s.defer = true;
    document.head.appendChild(s);
})();
