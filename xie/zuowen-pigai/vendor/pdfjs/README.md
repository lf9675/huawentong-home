PDF.js 6.4.299, legacy build, from the official `pdfjs-dist` npm package.

Mozilla PDF.js: https://github.com/mozilla/pdf.js

The library, worker, CMaps, fonts and WASM decoders are hosted here so school devices do not need a third-party CDN. See LICENSE and the licenses within the resource directories.

To update, pin and verify a supported release, copy `legacy/build/pdf.min.mjs`, `legacy/build/pdf.worker.min.mjs`, `LICENSE`, `cmaps/`, `standard_fonts/` and `wasm/`. Test scanned PDFs, Chinese text, page rotation, password errors and iPad compatibility before publishing.
